import json
import re
from pathlib import Path
from queue import LifoQueue

import jinja2

from ..common import repo_url
from .jsonschema import JSONSchema
from .markdown import MDCodeBlock, MDWriter

template_loader = jinja2.FileSystemLoader(searchpath=Path(__file__).parent / "templates/")
template_env = jinja2.Environment(loader=template_loader, autoescape=False, trim_blocks=True, lstrip_blocks=True)


def human_to_slugcase(text):
    return text.lower().replace(" ", "-")


class ValidationError(Exception):
    def __init__(self, missing_field, schema):
        if schema.refd_schema:
            message = f"Missing '{missing_field}' in '{schema.path}' or '{schema.refd_schema.path}'"
        else:
            message = f"Missing '{missing_field}' in '{schema.path}'"

        super().__init__(message)


def _validate_schema(schema):
    required_fields = ["type", "title", "description"]

    for field in required_fields:
        if getattr(schema, field) is None:
            raise ValidationError(field, schema)

    if schema.type == "array":
        if not schema.item_schema:
            raise ValidationError("items", schema)

        for field in required_fields:
            if getattr(schema.item_schema, field) is None:
                raise ValidationError(field, schema.item_schema)


def _example_text(example, simple=False):
    def json_text(d, simple):
        if not simple:
            return json.dumps(d, indent=4)

        new_d = {}
        for key, value in d.items():
            if isinstance(value, list):
                new_d[key] = "$$arr$$"
            elif isinstance(value, dict):
                new_d[key] = "$$obj$$"
            else:
                new_d[key] = value

        text = json.dumps(new_d, indent=4)
        text = text.replace('"$$obj$$"', "{...}")
        text = text.replace('"$$arr$$"', "[...]")

        return text

    if example is None:
        return None

    if isinstance(example, dict):
        return json_text(example, simple=simple)

    return json.dumps(example)


def _schema_repo_link(schema):
    return repo_url(
        file_path="/schemas/" + schema.file_name, line_start=schema.file_line_start, line_end=schema.file_line_end
    )


def _info_block(schema, type_text=None):
    template = template_env.get_template("info-block.jinja")
    functions = {
        "example_text": _example_text,
        "schema_repo_link": _schema_repo_link,
    }

    raw = template.render(schema=schema, type_text=type_text, **functions)
    raw = "\n".join([line.strip("\t") for line in raw.split("\n")])  # strip indents line by line

    return raw


def _info_cell(schema, type_text=None):
    info_block = _info_block(schema, type_text=type_text)
    template = template_env.get_template("info-cell.jinja")

    raw = template.render(schema=schema, info_block=info_block)
    raw = "\n".join([line.strip("\t") for line in raw.split("\n")])  # strip indents line by line

    return raw


def _property_row(schema, queue):
    _validate_schema(schema)

    type_text = ""
    type_link = ""
    key_text = f"`{schema.key}`"

    if schema.type == "object":
        queue.put(schema.primary_path)
        type_link = block_link(schema.refd_schema.title or schema.title)

    if schema.type == "array":
        key_text = f"`{schema.key}[]`"

        if schema.item_schema.type == "object":
            queue.put(schema.item_schema.primary_path)
            type_link = block_link(schema.item_schema.refd_schema.title or schema.item_schema.title)

    if schema.oneOf:
        queue.put(schema.primary_path)
        type_link = block_link(schema.title)

    if schema.type == "array":
        type_text += f"array of: `{schema.item_schema.type}`"
    else:
        type_text += f"`{schema.type}`"

    if type_link:
        type_text += f"&nbsp;&nbsp;({type_link})"
    elif schema.format:
        type_text += f"&nbsp;&nbsp;(`{schema.format}`)"

    info_cell = _info_cell(schema, type_text=type_text)

    return {
        "Property": key_text,
        "Description": info_cell,
    }


def schema_object_to_md(schema, md, queue):
    print(f"\tBuilding '{schema.title}'")
    _validate_schema(schema)

    md.push_heading(2, schema.title)

    info_block = _info_block(schema)

    md.push_paragraph(info_block)

    if schema.example is not None:
        codeblock = MDCodeBlock(_example_text(schema.example), language="json")
        md.push_admonition(codeblock, type="example", title="Example", collapsible=True, start_expanded=False)

    rows = []

    for property_schema in schema.properties_schemas:
        rows.append(_property_row(property_schema, queue))

    if not rows:
        print(f"\tWARNING: No fields defined for '{schema.title}'")
        return

    md.push_table(rows, class_="definitions")


def schema_oneOf_to_md(schema, md, queue):
    print(f"\tBuilding '{schema.title}'")
    _validate_schema(schema)

    md.push_heading(2, schema.title)
    md.push_paragraph(schema.description)

    rows = []

    if all((s.const is not None for s in schema.oneOf)):
        for one_schema in sorted(schema.oneOf, key=lambda s: s.const):
            _validate_schema(one_schema)

            rows.append(
                {
                    schema.title: f"`{one_schema.const}`",
                    "Description": _info_cell(one_schema),
                }
            )
    else:
        for one_schema in schema.oneOf:
            rows.append(_property_row(one_schema, queue))

    if not rows:
        print(f"\tWARNING: No fields defined for '{schema.title}'")
        return

    md.push_table(rows, class_="definitions")


def block_link(title):
    return f"[{title}](#{human_to_slugcase(title)})"


class JSONSchemaRenderer:
    def __init__(self):
        self.blocks = LifoQueue()

    def render_md(self, schema_path, output_path, file_alias=None):
        print(f"Processing schema '{schema_path}'")
        schema_path = Path(schema_path)

        self.schema = JSONSchema.from_file(schema_path)

        self.blocks = LifoQueue()
        self.visited = set()

        md = MDWriter()

        schema_file_name = schema_path.name
        file_name = file_alias or schema_file_name.replace(".schema.json", ".json")

        md.push_comment(
            f"Don't modify this file directly.\nThis file is automatically generated from '{schema_file_name}'."
        )
        md.push_heading(1, f"**`{file_name}`** format definition")

        repo_file_url = repo_url(file_path="/schemas/" + schema_file_name)
        md.push_admonition(
            f"This page has been automatically generated from [`{schema_file_name}`]({repo_file_url}).", type="info"
        )

        self.blocks.put("#")

        while not self.blocks.empty():
            path = self.blocks.get()
            schema = self.schema.get(path)
            _validate_schema(schema)

            if schema.primary_path in self.visited:
                print(f"\tSkipping '{path}' (already visited)")
                continue

            self.visited.add(schema.primary_path)

            if schema.oneOf is not None:
                schema_oneOf_to_md(schema, md, self.blocks)
            elif schema.type == "object":
                schema_object_to_md(schema, md, self.blocks)
            else:
                raise ValueError(f"Could not parse block {schema.path}")

        if output_path is None:
            return md.raw

        with open(output_path, "w") as f:
            f.write(md.raw)
