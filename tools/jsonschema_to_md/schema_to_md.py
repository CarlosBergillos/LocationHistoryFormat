import json
import re
from pathlib import Path
from queue import LifoQueue

from ..common import repo_url
from .jsonschema import JSONSchema
from .markdown import MDWriter


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


def _property_row(schema, queue):
    _validate_schema(schema)

    type_text = ""
    type_link = ""
    info_text = ""
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

    info_text += f'<span class="bold">{type_text}</span>'

    if "added" in schema.raw_schema:
        info_text += "\n"
        info_text += f"<span class=\"mdx-added\">:octicons-tag-24: *Added {schema.raw_schema['added']}.*</span>"

    if "removed" in schema.raw_schema:
        info_text += "\n"
        info_text += f"<span class=\"mdx-removed\">:octicons-tag-24: *Removed {schema.raw_schema['removed']}.*"

        if "replacedBy" in schema.raw_schema:
            replaced_by = schema.get(schema.raw_schema["replacedBy"])

            info_text += f" Replaced by `{replaced_by.key}`."

        info_text += "</span>"

    info_text += "\n\n"
    info_text += schema.description or ""

    if schema.example and schema.type != "object":
        info_text += "\n\n"
        info_text += f"*Example:* `{_example_text(schema.example)}`"

    if "helpWanted" in schema.raw_schema:
        help_wanted_msg = ""
        help_wanted_msg += schema.raw_schema["helpWanted"].replace("\n", " ")

        section_link = repo_url(
            file_path="/schemas/" + schema.file_name, line_start=schema.file_line_start, line_end=schema.file_line_end
        )
        help_wanted_msg += f" Contributions to improve this [are welcome]({section_link})."

        info_text += "\n\n"
        info_text += f'<span class="mdx-help">:octicons-tag-16: **Help Wanted:**</span> *{help_wanted_msg}*'

    return {
        "Property": key_text,
        "Description": info_text,
    }


def schema_object_to_md(schema, md, queue):
    print(f"\tBuilding '{schema.title}'")
    _validate_schema(schema)

    md.push_heading(2, schema.title)

    info_text = schema.description

    if "helpWanted" in schema.raw_schema:
        help_wanted_msg = ""
        help_wanted_msg += schema.raw_schema["helpWanted"].replace("\n", " ")

        section_link = repo_url(
            file_path="/schemas/" + schema.file_name, line_start=schema.file_line_start, line_end=schema.file_line_end
        )
        help_wanted_msg += f" Contributions to improve this [are welcome]({section_link})."

        info_text += "\n\n"
        info_text += f'<span class="mdx-help">:octicons-tag-16: **Help Wanted:**</span> *{help_wanted_msg}*'

    md.push_paragraph(info_text)

    # if schema.example:
    #     md.push_codeblock(_example_text(schema.example), 'json', 'Example')

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

    if not all(("const" in b for b in schema.oneOf)):
        raise NotImplementedError("Only const values are currently supported in 'oneOf'.")

    for obj in sorted(schema.oneOf, key=lambda b: b["const"]):
        rows.append(
            {
                schema.title: f"`{obj['const']}`",
                "Description": obj["description"],
            }
        )

    if not rows:
        print(f"\tWARNING: No fields defined for '{schema.title}'")
        return

    md.push_table(rows, class_="definitions")


def block_link(title):
    return f"[{title}](#{human_to_slugcase(title)})"


class JSONSchemaRenderer:
    def __init__(self):
        self.blocks = LifoQueue()

    def render_md(self, schema_path, output_path):
        print(f"Processing schema '{schema_path}'")
        schema_path = Path(schema_path)

        self.schema = JSONSchema.from_file(schema_path)

        self.blocks = LifoQueue()
        self.visited = set()

        md = MDWriter()

        schema_file_name = schema_path.name
        file_name = schema_file_name.replace(".schema.json", ".json")

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

            if schema.type == "object":
                schema_object_to_md(schema, md, self.blocks)
            elif schema.oneOf is not None:
                schema_oneOf_to_md(schema, md, self.blocks)
            else:
                raise ValueError(f"Could not parse block {schema.path}")

        if output_path is None:
            return md.raw

        with open(output_path, "w") as f:
            f.write(md.raw)
