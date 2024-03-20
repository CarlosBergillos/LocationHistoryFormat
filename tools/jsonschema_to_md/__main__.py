"""This script generates a Markdown file for a given input JSON schema.
"""


import argparse
import logging
from pathlib import Path

from rich.logging import RichHandler

from .jsonschema import JSONSchemaError
from .schema_to_md import JSONSchemaRenderer, ValidationError


def main():
    parser = argparse.ArgumentParser(
        prog="jsonschemas_to_md", description="Generate a Markdown file for a given input JSON schema."
    )
    parser.add_argument("input", help="Input JSON schema.", type=str)
    parser.add_argument("-o", "--output", help="Path for the output Markdown file.", type=str)
    parser.add_argument("-t", "--title", help="Title for the output Markdown file.", type=str)

    args = parser.parse_args()

    inp = Path(args.input)

    schema_filename = inp.name
    json_filename = schema_filename.replace(".schema.json", ".json")
    md_filename = json_filename + ".md"

    out = args.output or md_filename
    title = args.title

    logging.basicConfig(level=logging.NOTSET, format="%(message)s", datefmt="[%X]", handlers=[RichHandler(show_path=False)])
    logger = logging.getLogger(__name__)

    try:
        JSONSchemaRenderer(logger=None).render_md(inp, out, title=title)
    except (JSONSchemaError, ValidationError) as e:
        logger.error(e)
        return 1
    except Exception as e:
        logger.exception(e)
        return 1
    else:
        return 0

if __name__ == "__main__":
    raise SystemExit(main())
