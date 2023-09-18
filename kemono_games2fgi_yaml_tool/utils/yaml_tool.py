from textwrap import dedent

from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import PreservedScalarString
from yaml import safe_load


# from gameyamlspiderandgenerator.util.fgi_yaml


def pss_dedent(x: str) -> PreservedScalarString:
    return PreservedScalarString(dedent(x))


fgi = YAML(typ=["rt", "string"])
fgi.indent(sequence=4, offset=2)
fgi.preserve_quotes = True
fgi.width = 4096


def dump_to_yaml(data: dict) -> str:
    if "brief-description" in data:
        data["brief-description"] = pss_dedent(data["brief-description"])
    data["description"] = pss_dedent(data["description"])
    temp = fgi.dump_to_string(data)
    for i in list(data.keys())[1:]:
        temp = temp.replace("\n" + i, "\n\n" + i)
    return temp.replace("description: |-", "description: |")


def load_yaml(path: str) -> dict:
    with open(path, encoding="utf-8") as fp:
        data = safe_load(fp.read())
    return data
