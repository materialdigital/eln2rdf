import argparse
import json
import logging
import os
import sys
import urllib.parse
import warnings
import zipfile
from io import BytesIO

import matplotlib.pyplot as plt
import networkx as nx
import yaml
from rdflib import Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

# Configure logging

logger = logging.getLogger(__name__)


def get_group_name(json_data, suffix="", default="", 
separator="-"):
    """
    Retrieves the name of the first group from the JSON data.

    Args:
        json_data (list[dict]): A list of dictionaries 
containing data.
        suffix (str, optional): A suffix to append to the 
group name. Defaults to "".
        default (str, optional): Default value to return if 
no group is found. Defaults to "".
        separator (str, optional): Separator between the 
group name and suffix. Defaults to "-".

    Returns:
        str: The group name with the specified suffix or the 
default value.
    """
    try:
        for item in json_data:
            if item.get('category', '') == 'Group':
                return f"{item['title']}{separator}{suffix}"
    except KeyError:
        pass
    warnings.warn(f"Group name is missing. Skipping this 
data.")
    return default


def json_data_from_zip_generator(zip_file, pattern):
    """
    A generator that yields the content of all JSON files 
within a zip archive
    that match a given pattern.

    Parameters:
    - zip_file: file object or Path to the zip archive.
    - pattern: Pattern to match the JSON file names within 
the archive. (currently matched with endswith() method)

    Yields:
    - Tuple: A tuple containing the name of the JSON file and 
its content as a Python dictionary.
    """
    try:
        with zipfile.ZipFile(zip_file, 'r') as z:
            for file_name in z.namelist():
                if "__MACOSX" in file_name:
                    continue
                if file_name.endswith(pattern):
                    try:
                        with z.open(file_name) as f:
                            data = json.load(f)
                            logger.info(f"Processing file 
{file_name}")
                            yield file_name, data
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error decoding JSON 
from file {file_name}: {e}")
                    except Exception as e:
                        logger.warning(f"Error processing 
file {file_name}: {e}")

                elif file_name.endswith('.eln'):  # Handle 
nested zip files
                    with z.open(file_name) as 
nested_zip_file:
                        nested_zip_bytes = 
BytesIO(nested_zip_file.read())
                        try:
                            # Recursively process the nested 
zip file
                            logger.info(f"Processing ELN 
export: ({file_name})")
                            yield from 
json_data_from_zip_generator(nested_zip_bytes, pattern)
                        except Exception as e:
                            logger.warning(f"Error processing 
nested zip file ({file_name}): {e}")
    except zipfile.BadZipFile as e:
        logger.warning(f"BadZipFile error ({zip_file}): {e}")
    except FileNotFoundError as e:
        logger.warning(f"FileNotFoundError ({zip_file}): 
{e}")
    except Exception as e:
        logger.warning(f"An unexpected error occurred: {e}")


def parse_json_export(json_data, institute="Sample 
Institute"):
    """
    Extracts metadata from the JSON export of elabFTW 
experiments.

    Args:
        json_data (dict): A dictionary containing metadata 
and experiment data.
        institute (str, optional): The name of the institute 
conducting the experiments.
            Defaults to "Sample Institute".

    Returns:
        dict: A dictionary containing metadata from one or 
more experiments.
            Each entry includes fields such as 'elabid', 
'group', 'Institute', 'LastName',
            'experiments_links', and 'data_completeness'.

    This function processes the input JSON data exported from 
elabFTW, extracting relevant metadata
    for experiments. It updates the metadata with additional 
information and returns a structured dictionary.

    Note:
        If the structure of the input JSON files is not as 
expected, the function may not work correctly.
    """

    elabid = json_data.get("elabid", "")

    metadata = {
        "elabid": elabid,
        "group":  get_group_name(json_data['items_links'], 
suffix=elabid[:4]),
        "Institute": institute,
        "LastName": json_data.get('lastname', ""),
        "experiments_links": 
json_data.get('experiments_links', []),
        "fields": json_data['metadata']['extra_fields']
    }

    if "" in metadata.values():
        metadata["data_completeness"] = "incomplete"
    else:
        metadata["data_completeness"] = "complete"

    return metadata


def sanitize_uri_component(component):
    """Sanitize a URI component by replacing spaces with 
underscores and escaping unsafe characters."""
    component = component.replace(" ", "_") 
    return urllib.parse.quote(component, safe='_')  


def bind_prefixes_to_graph(g, namespaces):
    for prefix, uri in namespaces.items():
        logger.debug(f"Binding prefix {prefix} to URI {uri}")
        g.bind(prefix, Namespace(uri))


def resolve_string_to_uri(string, namespaces):
    # Split the string on the first occurrence of a colon
    if ":" in string:
        prefix, local_part = string.split(":", 1)
        # Check if the prefix exists in the namespaces 
dictionary
        if prefix in namespaces:
            # Return the URIRef constructed using the 
Namespace object
            return namespaces[prefix][local_part]
    # If no prefix matches or no colon is present, treat it 
as a full URIRef
    return URIRef(string)


def process_node(node_mapping, g, namespaces=None, elabid="",
                 unit_namespace="qudt", unit_predicate=None, 
value_predicate=None, **kwargs):

    fields = kwargs.get('fields', {})
    subject_template = node_mapping['subject_template']
    field_name =  node_mapping.get('json_field')
    if field_name in kwargs:
        field_data = {'value': kwargs[field_name]}
    else:
        field_data = fields.get(field_name, {})

    subject_str = 
subject_template.format(elabid=sanitize_uri_component(elabid))
    subject = resolve_string_to_uri(subject_str, namespaces)
    # Add types
    for rdf_type in node_mapping.get('types', []):
        g.add((subject, RDF.type, 
resolve_string_to_uri(rdf_type, namespaces)))

    # Add unit and value predicates if they exist
    if 'unit' in field_data:
        unit_uri = 
namespaces[unit_namespace][sanitize_uri_component(field_data['unit'])]
        g.add((subject, unit_predicate, unit_uri))
    if 'value' in field_data:
        value = field_data['value']
        datatype = field_data.get('type', 'string')
        try:
            if datatype == 'number':
                literal = Literal(float(value), 
datatype=XSD.float)
            else:
                literal = Literal(value, datatype=XSD.string)
        except ValueError:
            logger.warning(f"Could not convert value 
'{value}' to datatype {datatype}. Using string.")
            literal = Literal(value, datatype=XSD.string)
        g.add((subject, value_predicate, literal))
    return subject


def process_edges(g, edges, nodes_dict, namespaces):
    # Iterate over predicates in the edges mapping
    for predicate, source_targets in edges.items():
        # Loop through each source node and its target nodes
        for source_node, target_nodes in 
source_targets.items():
            # Get the source node URIRef from the nodes 
dictionary
            source_uri = nodes_dict.get(source_node)
            # Loop through each target node
            for target_node in target_nodes:
                # Get the target node URIRef from the nodes 
dictionary
                target_uri = nodes_dict.get(target_node)
                # Add the edge to the graph
                g.add((source_uri, 
resolve_string_to_uri(predicate, namespaces), target_uri))


def plot_rdf_graph(rdf_graph, image_filename):
    # Create a NetworkX graph
    nx_graph = nx.DiGraph()

    # Convert RDF triples to NetworkX graph
    for subj, pred, obj in rdf_graph:
        nx_graph.add_edge(subj, obj, label=pred)

    # Set positions for the nodes in the graph
    pos = nx.spring_layout(nx_graph, k=0.5, iterations=50)

    # Draw the nodes and edges
    plt.figure(figsize=(12, 12))
    nx.draw(nx_graph, pos, with_labels=True, node_size=3000, 
node_color="lightblue", font_size=10, font_weight="bold", 
arrows=True)

    # Draw edge labels (predicates)
    edge_labels = {(u, v): d['label'].split('/')[-1] for u, 
v, d in nx_graph.edges(data=True)}
    nx.draw_networkx_edge_labels(nx_graph, pos, 
edge_labels=edge_labels, font_color='red')

    # Save the plot to an image file
    plt.savefig(image_filename)

    # Close the plot to avoid display
    plt.close()


def process_data_with_mapping(g, data_item, data_mapping):

    nodes = dict()
    namespaces =  {p: Namespace(u) for p, u in 
g.namespaces()}
    general_config = {
        "unit_namespace": data_mapping.get('unit_namespace', 
'qudt'),
        "unit_predicate": 
resolve_string_to_uri(data_mapping.get('unit_predicate'), 
namespaces),
        "value_predicate": 
resolve_string_to_uri(data_mapping.get('value_predicate'), 
namespaces)
    }
    # Process each node
    for node_name, node_mapping in 
data_mapping['nodes'].items():
        node_subj = process_node(node_mapping, g, 
namespaces=namespaces, **data_item, **general_config)
        nodes[node_name] = node_subj

    # Process edges
    process_edges(g, data_mapping.get('edges', {}), nodes, 
namespaces)


def main():
    parser = argparse.ArgumentParser(description='Convert ELN 
export to RDF Turtle format.')

    # Required positional arguments
    parser.add_argument('eln_export', type=str, help='Path to 
the ELN export file or folder')

    # Optional arguments
    parser.add_argument('-o', '--output', type=str,
                        help='Name of the output Turtle file. 
Defaults to basename of input + .ttl')
    parser.add_argument('-k', '--keymap', type=str, 
required=True, help='Path to the YAML keymap file')
    parser.add_argument('--plot', type=str, help='Plot the 
RDF graph as an image')
    parser.add_argument('--pattern', type=str, 
default='ftw.json',
                        help='Pattern to match JSON files in 
the ELN export (default: ftw.json)')
    parser.add_argument('--loglevel', type=str, 
default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 
'ERROR', 'CRITICAL'],
                        help='Set the logging level (default: 
INFO)')

    args = parser.parse_args()

    # Configure logging level based on user input
    logging.basicConfig(level=getattr(logging, 
args.loglevel.upper()))

    # Assign arguments to variables
    eln_export = args.eln_export
    output_file = args.output or 
os.path.splitext(os.path.basename(eln_export))[0] + '.ttl'
    keymap_file_path = args.keymap
    pattern = args.pattern
    image_filename = args.plot

    # Load the keymap
    try:
        with open(keymap_file_path, 'r') as f:
            keymap = yaml.safe_load(f)
            logger.info(f"Keymap loaded from 
{keymap_file_path}")
    except Exception as e:
        logger.error(f"An error occurred while loading the 
keymap: {e}")
        sys.exit(1)

    try:
        # Create a fresh RDF graph each time
        data_graph = Graph()

        # Bind the prefixes to the RDF graph
        bind_prefixes_to_graph(data_graph, 
keymap['namespaces'])

        # Process each file in the ELN export
        for file_name, json_data in 
json_data_from_zip_generator(eln_export, pattern):
            # Parse the JSON export data using 
parse_json_export
            elab_data = parse_json_export(json_data[0])
            process_data_with_mapping(data_graph, elab_data, 
keymap)

        # Serialize the graph to a Turtle file
        data_graph.serialize(destination=output_file, 
format='turtle')
        logger.info(f"RDF graph serialized to {output_file}")

        # Plot RDF graph if --plot option is enabled
        if args.plot:
            plot_rdf_graph(data_graph, image_filename)
            logger.info(f"RDF graph plotted and saved as 
{image_filename}")

    except Exception as e:
        logger.error(f"An error occurred during data 
generation/processing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
