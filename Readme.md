# ELN2RDF

This repository contains Python code that converts the export of an Electronic Lab Notebook (ELN) to the Resource Description Framework (RDF) in Turtle format. The code is based on the [rdflib](https://rdflib.readthedocs.io/en/stable/) library and provides an optional feature to generate a visual plot of the RDF graph.

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
