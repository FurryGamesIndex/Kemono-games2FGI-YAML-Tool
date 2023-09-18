# Kemono Games to FGI YAML Tool

![License](https://img.shields.io/badge/license-MIT-blue.svg)

Convert game data from Kemono Games format to Furry Games Index (FGI) YAML format.

## Installation

Use [Poetry](https://python-poetry.org/) to install the tool:

```bash
git clone https://github.com/kaixinol/Kemono-games2FGI-YAML-Tool.git
cd Kemono-games2FGI-YAML-Tool
poetry install
```

## Usage

```bash
# Convert multiple game entries 
py -m kemono_games2fgi_yaml_tool -i INPUT_FOLDER_FGI INPUT_FOLDER_KEMONO -o OUTPUT_FOLDER --sm.ms YOUR_TOKEN 
# Convert a single YAML file 
py -m kemono_games2fgi_yaml_tool -s SINGLE_YAML_FILE -o OUTPUT_FOLDER --sm.ms YOUR_TOKEN
```


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
