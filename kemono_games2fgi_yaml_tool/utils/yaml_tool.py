from textwrap import dedent
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import PreservedScalarString


# from gameyamlspiderandgenerator.util.fgi_yaml

def pss_dedent(x: str) -> PreservedScalarString:
    return PreservedScalarString(dedent(x))


fgi = YAML(typ=["rt", "string"])
fgi.indent(sequence=4, offset=2)
fgi.preserve_quotes = True
fgi.width = 4096


def dump_to_yaml(data: dict) -> str:
    temp = fgi.dump_to_string(data)
    for i in list(data.keys())[1:]:
        temp = temp.replace("\n" + i, "\n\n" + i)
    return temp.replace("description: |-", "description: |")

