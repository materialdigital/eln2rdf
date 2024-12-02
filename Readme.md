# ELN2RDF

This repository contains a [Jupyter Notebook script](https://github.com/materialdigital/eln2rdf) designed to transform mechanical test data from an Electronic Lab Notebook (ELN) into RDF format, leveraging Semantic Web technologies (SWT) for enhanced data management.

### Key Features
- **Data Transformation Pipeline**: The script automates the conversion of experimental data into RDF format, utilizing semantic concepts and ontologies to ensure a standardized and interoperable data representation.
- **Enhanced Data Interoperability**: By integrating data stored in an ELN with semantic technologies, the pipeline improves the richness, contextuality, and usability of experimental data, facilitating better integration with diverse data sources.
- **Improved Efficiency**: Automating data mapping reduces manual processing efforts, minimizing potential errors and enhancing scalability in handling large volumes of data. This user-friendly approach allows researchers to focus on expert analysis rather than data transfer tasks.
- **Educational Impact**: The pipeline has been successfully utilized by students with minimal prior experience in semantic data management, demonstrating its ease of use and effectiveness in practical lab settings.

This approach underscores the importance of modern data management techniques in accelerating scientific discovery and innovation, by unlocking the full potential of research data through advanced semantic technologies. 
As one example, tensile test results and the corresponding [Tensile Test Ontology (TTO)](https://github.com/MarkusSchilling/application-ontologies/tree/a96ac95e03df87b906226742cac75fd4f99faf5e/tensile_test_ontology_TTO) in version 2.0.7 developed in the frame of the joint project [Platform MaterialDigital (PMD)](https://materialdigital.de/) were used.

## Function

This script takes a path to a data directory and an output file name as inputs, and generates an RDF graph from the data. The graph is then serialized in turtle format (TTL) and saved to the output file.


## Scientific Publication

When addressing the script given in this repository transforming ELN to RDF data, please refer to and cite the following publication which provides enhanced information on and in-depth insights into the script and its development:

*M. Schilling, S. Bruns, B. Bayerlein, J. Kryeziu, J. Schaarschmidt, J. Waitelonis, P. D. Portella, K. Durst, Advanced Engineering Materials 2024, DOI: https://doi.org/10.1002/adem.202401527.*

Bibtex:
```
@article{Schilling2024,
   author = {Schilling, Markus and Bruns, Sebastian and Bayerlein, Bernd and Kryeziu, Jehona and Schaarschmidt, Jörg and Waitelonis, Jörg and Dolabella Portella, Pedro and Durst, Karsten},
   title = {Seamless Science: Lifting Experimental Mechanical Testing Lab Data to an Interoperable Semantic Representation},
   journal = {Advanced Engineering Materials},
   pages = {2401527},
   keywords = {electronic laboratory notebooks, mechanical testing, ontologies, semantic data integration, semantic web technologies},
   DOI = {10.1002/adem.202401527},
   url = {https://doi.org/10.1002/adem.202401527},
   eprint = {https://onlinelibrary.wiley.com/doi/pdf/10.1002/adem.202401527},
   year = {2024},
   type = {Journal Article}
}
```
available open access at: [Advanced Engineering Materials](https://doi.org/10.1002/adem.202401527).
  
This publication offers valuable insights into the purpose, usage, and development process of the transformation script given in this repository. These aspects are illustrated by the example of tensile tests performed by undergraduate students at the TU Darmstadt. This pulication may be an essential reference for users and contributors.

## Prerequisites

Before running this script, we strongly recommend creating and activating a Python virtual or conda environment and installing the necessary Python packages in this environment. Refer to the [official Python documentation](https://docs.python.org/3/library/venv.html) for more information on how to create a virtual environment or the [conda documentation](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html) for conda environments.

### Install Dependencies

After activating the environment, install the dependencies by running:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Command:
To convert an ELN export into RDF Turtle format, run:
```bash
python eln_to_rdf.py <eln_export> --keymap <keymap.yaml>
```

- `eln_export`: Path to the ELN export file (e.g., a `.zip` file) or directory containing JSON data.
- `--keymap`: Path to the YAML keymap configuration file.

### Optional Arguments:

- `-o, --output <output_file>`: Name of the output Turtle file. If not provided, the default is the basename of the input ELN export file with a `.ttl` extension.

- `--pattern <pattern>`: Pattern to match JSON files within the ELN export (default: `ftw.json`). This allows you to customize the selection of JSON files to process.

- `--plot`: Generate and save a visual plot of the RDF graph as an image. The image will be saved in the same location as the output Turtle file, with a `.png` extension.

- `--loglevel <level>`: Set the logging level. Available options are `DEBUG`, `INFO`, `WARNING`, `ERROR`, and `CRITICAL`. The default level is `INFO`.
