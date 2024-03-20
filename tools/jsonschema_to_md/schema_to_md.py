import json
import logging
from pathlib import Path
from queue import Queue
import re

import jinja2

from ..common import repo_url
from .jsonschema import JSONSchema, EmptyJSONSchema
from .markdown import MDCodeBlock, MDWriter

template_loader = jinja2.FileSystemLoader(searchpath=Path(__file__).parent / "templates/")
template_env = jinja2.Environment(loader=template_loader, autoescape=False, trim_blocks=True, lstrip_blocks=True)


class ValidationError(Exception):
    def __init__(self, missing_field, schema):
        if schema.refd_schema:
            message = f"Missing '{missing_field}' in '{schema.path}' or '{schema.refd_schema.path}'"
        else:
            message = f"Missing '{missing_field}' in '{schema.path}'"

        super().__init__(message)


class JSONSchemaRenderer:
    def __init__(self, logger=None):
        if logger is not None:
            self.logger = logger
        else:
            logging.basicConfig(level=logging.NOTSET, format="%(message)s", datefmt="[%X]")
            self.logger = logging.getLogger(__name__)

    def _validate_schema(self, schema, required_fields=["type", "title", "description"]):
        for field in required_fields:
            if getattr(schema, field) is None:
                raise ValidationError(field, schema)

        if schema.type == "array":
            if not schema.item_schema:
                raise ValidationError("items", schema)
            
            if schema.item_schema.type == "object":
                self._validate_schema(schema.item_schema)
            else:
                self._validate_schema(schema.item_schema, required_fields=["type"])

    def _example_text(self, example, simple=False):
        def json_text(d, simple):
            if not simple:
                return json.dumps(d, indent=4)

            def recurse(d):
                if isinstance(d, list):
                    new_l = []
                    for value in d:
                        if isinstance(value, list):
                            new_d[key] = "$$arr$$"
                        elif isinstance(value, dict):
                            new_d[key] = "$$obj$$"
                        else:
                            new_d[key] = recurse(value)

                    return new_l
                elif isinstance(d, dict):
                    new_d = {}
                    for key, value in d.items():
                        if isinstance(value, list):
                            new_d[key] = "$$arr$$"
                        elif isinstance(value, dict):
                            new_d[key] = "$$obj$$"
                        else:
                            new_d[key] = recurse(value)

                    return new_d
                else:
                    return d

            new_d = recurse(d)

            text = json.dumps(new_d, indent=4)
            text = text.replace('"$$obj$$"', "{...}")
            text = text.replace('"$$arr$$"', "[...]")

            return text

        if example is None:
            return None

        if isinstance(example, dict):
            return json_text(example, simple=simple)

        return json.dumps(example)

    def _schema_repo_link(self, schema):
        return repo_url(
            file_path="/schemas/" + schema.file_name, line_start=schema.file_line_start, line_end=schema.file_line_end
        )

    def _schema_fragment(self, schema, section=False):
        # when section=True the fragment should link to the main section (if it exists). We indicate this by using a trailing slash.
        # when section=False the fragment should link to the table row where it is used. We indicate this by not using a trailing slash.

        fragment_id = schema.path.removeprefix("#")

        if section:
            return fragment_id + "/"

        return fragment_id

    def _schema_link(self, schema, section=False):
        fragment = self._schema_fragment(schema, section=section)

        if section:
            return f"[{schema.title}](#{fragment})"
        else:
            return f"[`{schema.key}`](#{fragment})"

    def _info_block(self, schema, type_text=None):
        template = template_env.get_template("info-block.jinja")
        functions = {
            "example_text": self._example_text,
            "schema_link": self._schema_link,
            "schema_repo_link": self._schema_repo_link,
            "process_description": self._process_description,
        }

        raw = template.render(schema=schema, type_text=type_text, **functions)
        raw = "\n".join([line.strip("\t") for line in raw.split("\n")])  # strip indents line by line

        return raw

    def _info_cell(self, schema, type_text=None):
        info_block = self._info_block(schema, type_text=type_text)
        template = template_env.get_template("info-cell.jinja")

        raw = template.render(schema=schema, info_block=info_block)
        raw = "\n".join([line.strip("\t") for line in raw.split("\n")])  # strip indents line by line

        return raw

    def _process_description(self, root_schema, description):
        def reflink(match):
            section = bool(match.group(1))
            path = match.group(2)
            schema = root_schema.get(path)

            return self._schema_link(schema, section=section)

        # replace references like '[#/$defs/activitySegment]' with a link to the object/property.
        # if it starts with a !, e.g. '![#/$defs/activitySegment]' then use title for the link instead of the key (via use_title=True).
        description = re.sub(r"(!)?\[(#\/[^\s\[\]]*)\]", reflink, description)

        return description

    def _property_row(self, schema, queue):
        self._validate_schema(schema)

        type_text = ""
        type_link = ""
        key_text = f"`{schema.key}`"

        if schema.type == "object":
            queue.put(schema.primary_path)
            type_link = self._schema_link(schema.refd_schema or schema, section=True)

        if schema.type == "array":
            key_text = f"`{schema.key}\u200B[]`"

            if schema.item_schema.type == "object":
                queue.put(schema.item_schema.primary_path)
                type_link = self._schema_link(schema.item_schema.refd_schema or schema.item_schema, section=True)

        if schema.oneOf:
            queue.put(schema.primary_path)
            type_link = self._schema_link(schema.refd_schema or schema, section=True)

        if schema.type == "array":
            type_text += f"array of: `{schema.item_schema.type}`"
        else:
            type_text += f"`{schema.type}`"

        if type_link:
            type_text += f"&nbsp;&nbsp;({type_link})"
        elif schema.format:
            type_text += f"&nbsp;&nbsp;(`{schema.format}`)"

        info_cell = self._info_cell(schema, type_text=type_text)

        return {
            "Property": key_text + f' {{ id="{self._schema_fragment(schema, section=False)}" }}',
            "Description": info_cell,
        }

    def schema_object_to_md(self, schema, md, queue):
        n = len(schema.raw_properties)
        self.logger.info(f"Building '{schema.path}' ({n} {'property' if n==1 else 'properties'})")
        self._validate_schema(schema)

        md.push_heading(2, schema.title, id=self._schema_fragment(schema, section=True))

        info_block = self._info_block(schema)
        md.push_paragraph(info_block)

        if schema.example is not None:
            codeblock = MDCodeBlock(self._example_text(schema.example), language="json")
            md.push_admonition(codeblock, type="example", title="Example", collapsible=True, start_expanded=False)

        rows = []

        for property_schema in schema.properties_schemas:
            rows.append(self._property_row(property_schema, queue))

        if not rows:
            self.logger.warning(f"No properties defined for '{schema.path}'")
            return

        md.push_table(rows, class_="definitions")

    def schema_oneOf_to_md(self, schema, md, queue):
        n = len(schema.oneOf)
        self.logger.info(f"Building '{schema.path}' ({n} oneOf entries)")
        self._validate_schema(schema)

        md.push_heading(2, schema.title, id=self._schema_fragment(schema, section=True))

        info_block = self._info_block(schema)
        md.push_paragraph(info_block)

        rows = []

        if all(s.const is not None for s in schema.oneOf):
            # Special case where all options are const.
            for one_schema in sorted(schema.oneOf, key=lambda s: s.const):
                self._validate_schema(one_schema)

                rows.append(
                    {
                        schema.title: f'`{one_schema.const}` {{ id="{self._schema_fragment(one_schema, section=False)}" }}',
                        "Description": self._info_cell(one_schema),
                    }
                )
        elif all((s.type == "object" and len(s.properties_keys) == 1 for s in schema.oneOf)) and (
            len(schema.oneOf) == len(set(s.properties_keys[0] for s in schema.oneOf))
        ):
            # Special case where all options are objects with one distinct key.
            for one_schema in sorted(schema.oneOf, key=lambda s: s.properties_keys[0]):
                row = self._property_row(one_schema.properties_schemas[0], queue)
                rows.append(
                    {
                        "Single Property": row["Property"],
                        "Description": row["Description"],
                    }
                )
        else:
            for one_schema in schema.oneOf:
                rows.append(self._property_row(one_schema, queue))

        if not rows:
            self.logger.warning(f"No oneOf entries defined for '{schema.path}'")
            return

        md.push_table(rows, class_="definitions")

    def render_md(self, schema_path, output_path, title=None):
        self.logger.info(f"Processing schema '{schema_path}'")
        schema_path = Path(schema_path)

        self.schema = JSONSchema.from_file(schema_path)

        self.blocks = Queue()
        self.visited = set()

        md = MDWriter()

        schema_file_name = schema_path.name
        file_name = schema_file_name.replace(".schema.json", ".json")

        md.push_comment(
            f"Don't modify this file directly.\nThis file is automatically generated from '{schema_file_name}'."
        )
        md.push_heading(1, title or f"**`{file_name}`** Format Definition")

        repo_file_url = repo_url(file_path="/schemas/" + schema_file_name)
        md.push_admonition(
            f"This page has been automatically generated from the schema [`{schema_file_name}`]({repo_file_url}).",
            type="info",
        )

        if self.schema.raw_schema.get("extra_wip"):
            md.push_admonition(f"This schema is still work in progress.", type="info", title="WIP")

        self.blocks.put("#")

        while not self.blocks.empty():
            path = self.blocks.get()
            schema = self.schema.get(path)
            self._validate_schema(schema)

            if schema.primary_path in self.visited:
                self.logger.info(f"Skipping (already built) '{path}'")
                continue

            self.visited.add(schema.primary_path)

            if schema.oneOf is not None:
                self.schema_oneOf_to_md(schema, md, self.blocks)
            elif schema.type == "object":
                self.schema_object_to_md(schema, md, self.blocks)
            else:
                raise ValueError(f"Could not parse block {schema.path}")

        if output_path is None:
            return md.raw

        with open(output_path, "w") as f:
            f.write(md.raw)
