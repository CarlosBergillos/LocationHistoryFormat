import json
import re
from pathlib import Path
from queue import LifoQueue

from .markdown import MDWriter
from .jsonschema import JSONSchema

import pandas as pd
import yaml


def human_to_slugcase(text):
    return text.lower().replace(' ', '-')


def repo_url(path='./mkdocs.yml'):
    yaml.add_multi_constructor('tag:yaml.org,2002:python/name', lambda loader, suffix, node: None, Loader=yaml.SafeLoader)

    with open(path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config['repo_url']


def _property_row(schema, queue):
        type_text = ""
        type_link = ""
        info_text = ""
        key_text = f"`{schema.key}`"

        if schema.type == 'object':
            queue.put(schema.path)
            type_link = block_link(schema.refd_schema.title or schema.title)

        if schema.type == 'array':
            key_text = f"`{schema.key}[]`"

            if schema.item_schema.type == 'object':
                queue.put(schema.item_schema.path)
                type_link = block_link(schema.item_schema.refd_schema.title or schema.item_schema.title)

        if schema.oneOf:
            queue.put(schema.path)
            type_link = block_link(schema.title)

        if schema.type == 'array':
            type_text += f"array of: `{schema.item_schema.type}`"
        else:
            type_text += f"`{schema.type}`"

        if type_link:
            type_text += f"&nbsp;&nbsp;({type_link})"
        elif schema.format:
            type_text += f"&nbsp;&nbsp;(`{schema.format}`)"

        info_text += f"<span class=\"bold\">{type_text}</span>"
        
        if 'added' in schema.raw_schema:
            info_text += "\n"
            info_text += f"<span class=\"mdx-added\">:octicons-tag-24: *Added {schema.raw_schema['added']}.*</span>"

        if 'removed' in schema.raw_schema:
            info_text += "\n"
            info_text += f"<span class=\"mdx-removed\">:octicons-tag-24: *Removed {schema.raw_schema['removed']}.*"
            
            if 'replacedBy' in schema.raw_schema:
                replaced_by = schema.get(schema.raw_schema['replacedBy'])

                info_text += f" Replaced by `{replaced_by.key}`."

            info_text += "</span>"

        info_text += "\n\n"
        info_text += schema.description or ''

        if schema.example and schema.type != 'object':
            info_text += "\n\n"
            info_text += f"*Example:* `{schema.example}`"
        
        if 'helpWanted' in schema.raw_schema:
            help_wanted_msg = ""
            help_wanted_msg += schema.raw_schema['helpWanted'].replace('\n', ' ')
            help_wanted_msg += " Contributions to improve this are welcomed."

            info_text += "\n\n"
            info_text += f"<span class=\"mdx-help\">:octicons-tag-16: **Help Wanted:**</span> *{help_wanted_msg}*"

        return {
            'Field': key_text,
            'Description': info_text,
        }


def schema_object_to_md(schema, md, queue):
    print(f"\tBuilding '{schema.title}'")
    md.push_heading(2, schema.title)
    md.push_paragraph(schema.description)

    rows = []

    for property_schema in schema.properties_schemas:
        rows.append(_property_row(property_schema, queue))
    
    if not rows:
        print(f"\tWARNING: No fields defined for '{schema.title}'")
        return

    df = pd.DataFrame.from_records(rows)
    df.set_index('Field', drop=True, inplace=True)
    md.push_table(df, class_='definitions')


def schema_oneOf_to_md(schema, md, queue):
        print(f"\tBuilding '{schema.title}'")
        md.push_heading(2, schema.title)
        md.push_paragraph(schema.description)

        rows = []

        if not all(('const' in b for b in schema.oneOf)):
            raise NotImplementedError("Only const values are currently supported in 'oneOf'.")

        for obj in sorted(schema.oneOf, key=lambda b: b['const']):
            rows.append({
                'Field': f"`{obj['const']}`",
                'Description': obj['description'],
            })
        
        if not rows:
            print(f"\tWARNING: No fields defined for '{schema.title}'")
            return

        df = pd.DataFrame.from_records(rows)
        df.set_index('Field', drop=True, inplace=True)
        df.index.name = schema.title
        md.push_table(df, class_='definitions')


def block_link(title):
    return f"[{title}](#{human_to_slugcase(title)})"


class JSONSchemaRenderer:
    def __init__(self):
        self.blocks = LifoQueue()

    def render_md(self, schema_path, output_path):
        print(f"Processing schema '{schema_path}'")
        schema_path = Path(schema_path)

        with open(schema_path, 'r') as f:
            raw_schema = json.load(f)

        self.schema = JSONSchema(raw_schema)

        self.blocks = LifoQueue()
        self.visited = set()

        md = MDWriter()

        schema_file_name = schema_path.name
        file_name = schema_file_name.replace('.schema.json', '.json')

        md.push_comment(f"Don't modify this file directly.\nThis file is automatically generated from '{schema_file_name}'.")
        md.push_heading(1, f"**`{file_name}`** format definition")

        repo_file_url = repo_url() + '/tree/main/schemas/' + schema_file_name
        md.push_admonition(f"This page is automatically generated from [`{schema_file_name}`]({repo_file_url}).", type='info')

        self.blocks.put('#')

        while not self.blocks.empty():
            path = self.blocks.get()
            schema = self.schema.get(path)

            if schema.primary_path in self.visited:
                print(f"\tSkipping '{path}' (already visited)")
                continue

            self.visited.add(schema.primary_path)

            
            if schema.type == 'object':
                schema_object_to_md(schema, md, self.blocks)
            elif schema.oneOf:
                schema_oneOf_to_md(schema, md, self.blocks)
            else:
                raise ValueError()

        if output_path is None:
            return md.raw
        
        with open(output_path, 'w') as f:
            f.write(md.raw)
