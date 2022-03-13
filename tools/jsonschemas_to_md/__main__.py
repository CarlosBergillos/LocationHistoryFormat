import argparse
from pathlib import Path

from .schema_to_md import JSONSchemaRenderer


def main():
    parser = argparse.ArgumentParser(prog="jsonschemas_to_md", description="Transform a JSON schema into a Markdown file.")
    parser.add_argument("input", help="Input JSON schema.", type=str)
    parser.add_argument("-o", "--output", help="Path for the output Markdown file.", type=str)
    
    args = parser.parse_args()

    inp = Path(args.input)

    schema_filename = inp.name
    json_filename = schema_filename.replace('.schema.json', '.json')
    md_filename = json_filename + '.md'
    
    out = args.output or md_filename

    JSONSchemaRenderer().render_md(inp, out)

if __name__ == "__main__":
    main()
