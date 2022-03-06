import json
import re
from pathlib import Path
from queue import Queue

from tabulate import tabulate
import pandas as pd


# def camelcase_to_titlecase(text):
    # return re.sub(r'(?<!^)(?=[A-Z])', ' ', text).title()


def human_to_slugcase(text):
    return text.lower().replace(' ', '-')


def example(obj):
    if not obj.get('examples'):
        return None, False

    x = obj.get('examples')[0]

    if isinstance(x, dict):
        return json.dumps(x, indent=4), True

    return json.dumps(x), False


def get_ref(ref, schema):
    base, path = ref.split('#')
    parts = path.split('/')
    
    ret = schema
    for part in parts:
        if not part:
            continue

        ret = ret.get(part)
    
    if ret is None:
        raise ValueError(f"Did not find ref '{ref}'")

    ret['_key'] = part

    return part, ret


class MDWriter:
    def __init__(self):
        self.raw = ''
    
    def push_heading(self, level, text):
        assert level <= 6
        self.raw += f"{'#' * level} {text}\n\n"

    def push_paragraph(self, text, indent=False, block=False):
        if not text:
            text = '-'

        if indent:
            if block:
                text = text.replace('\n', '\n\t> ')
                text = text.replace('> \t<', '\t')  # admonition contents should not have '>', so we have flagged them with '<'.
                self.raw += f":\t> {text}\n\n"
            else:
                text = text.replace('\n', '\n\t')
                self.raw += f":\t{text}\n\n"
        else:
            self.raw += f"{text}\n\n"
    
    def push_comment(self, text):
        self.raw += f"<!---\n{text}\n-->\n\n"
    
    def push_table(self, table, class_=None):
        # table = table.applymap(lambda x: x.replace('\n', '<br>'))
        table = table.applymap(lambda x: x.replace('\n', '<p style="margin: 10px 0;"></p>'))

        if class_ is not None:
            self.raw +=f"<div class=\"{class_}\"></div>\n\n"  # note we cannot add a class to the table, we create a separate 'sentinel' div.

        self.raw += tabulate(table, headers="keys", showindex=True, tablefmt="pipe")
        self.raw += f"\n\n"


def block_link(block):
    return f"[{block['title']}](#{human_to_slugcase(block['title'])})"

class X:
    def __init__(self):
        self.blocks = Queue()

    def object_property_row(self, obj, key):
        example_text, is_block = example(obj)
        obj_ref = obj.get('$ref')
        obj_link = None
        obj_type = obj.get('type')
        rfd_obj = None
        arr_obj = None
        arr_obj_type = None
        rfd_arr_obj = None
        
        if obj_ref is not None:
            _, rfd_obj = get_ref(obj_ref, self.schema)
            obj_type = rfd_obj.get('type')
        
        # if 'title' not in obj:
        #     raise ValueError(f"Missing 'title' for field '{obj['_key']}'")

        # if obj_type is None:
        #     raise ValueError(f"Missing 'type' for field '{obj['_key']}'")

        if obj_type == 'object':
            self.blocks.put(('object', obj))
            obj_link = block_link(rfd_obj or obj)

        if obj_type == 'array':
            arr_obj = obj.get('items', {})
            arr_obj['_key'] = obj['_key']
            arr_obj_ref = arr_obj.get('$ref')
            arr_obj_type = arr_obj.get('type')
            arr_obj_link = None

            if arr_obj_ref is not None:
                _, rfd_arr_obj = get_ref(arr_obj_ref, self.schema)
                arr_obj_type = rfd_arr_obj.get('type')
                arr_obj = rfd_arr_obj

            if 'title' not in arr_obj:
                raise ValueError(f"Missing 'title' for field '{obj['_key']}'")

            if arr_obj_type is None:
                raise ValueError(f"Missing 'type' for field '{obj['_key']}'")

            if arr_obj_type == 'object':
                self.blocks.put(('object', arr_obj))
                obj_link = block_link(rfd_arr_obj or arr_obj)

            # md.push_paragraph(f"\tAn array of [`{next_key}`](#{human_to_slugcase(next_key)}) objects.")

            # obj_type = next_obj['type']
                
            key_text = f"`{key}[]`"
        else:
            key_text = f"`{key}`"

        if 'oneOf' in obj:
            self.blocks.put(('oneOf', obj))
            obj_link = block_link(obj)
        
        # if 'anyOf' in obj:
        #     self.blocks.put(obj['anyOf'][0])

        info = ""
        if obj_link is not None:
            info += f"<span class=\"bold\">`{arr_obj_type or obj_type}`&nbsp;&nbsp;({obj_link})</span>"
        else:
            info += f"<span class=\"bold\">`{obj_type}`</span>"
        
        if 'added' in obj:
            info += "\n"
            info += f"<span class=\"mdx-added\">:octicons-tag-24: *Added {obj.get('added')}.*</span>"

        if 'removed' in obj:
            info += "\n"
            info += f"<span class=\"mdx-removed\">:octicons-tag-24: *Removed {obj.get('removed')}.*"
            
            if 'replacedBy' in obj:
                next_obj, name = get_ref(obj.get('replacedBy'), self.schema)

                info += f" Replaced by [`{name}`](#{name})."

            info += "</span>"

        # info += "\n\n"
        # info += f"**{obj['title']}**"

        info += "\n\n"
        info += f"{obj.get('description', '')}"

        if 'oneOf' in obj and obj_link is not None:
            info += f" See {obj_link} for a list of possible values."

        if example_text and obj.get('type') != 'object':
            info += "\n\n"
            info += f"*Example:* `{example_text}`"
        
        if 'helpWanted' in obj:
            help_wanted_msg = ""
            help_wanted_msg += obj.get('helpWanted').replace('\n', ' ')
            help_wanted_msg += " Contributions to improve this section are welcomed."

            info += "\n\n"
            info += f"<span class=\"mdx-help\">:octicons-tag-24: **Help Wanted:**</span> *{help_wanted_msg}*"

        return {
            'Field': key_text,
            # 'title': obj['title'],
            # 'type': obj['type'],
            # 'example': example_text,
            'Description': info,
        }

        # is_leaf = obj.get('type') not in ['object', 'array']

    def oneOf_block(self, block, md):
        # self.rows[0]
        print(f"Building '{block['title']}'")
        md.push_heading(2, block['title'])
        md.push_paragraph(block.get('description'))

        rows = []

        if not all(('const' in b for b in block['oneOf'])):
            raise NotImplementedError("Only const values are currently supported in 'oneOf'.")

        for obj in sorted(block['oneOf'], key=lambda b: b['const']):
            rows.append({
                'Field': f"`{obj['const']}`",
                'Description': obj['description'],
            })
        
        if not rows:
            print(f"WARNING: No fields defined for '{block['title']}'")
            return

        df = pd.DataFrame.from_records(rows)
        df.set_index('Field', drop=True, inplace=True)
        df.index.name = block['title']
        md.push_table(df, class_='definitions')

    def object_block(self, block, md):        
        print(f"Building '{block['title']}'")
        md.push_heading(2, block['title'])
        md.push_paragraph(block.get('description'))

        rows = []

        if block['type'] == 'object':
            for key, obj in sorted(block.get('properties', {}).items()):
                obj['_key'] = key
                rows.append(self.object_property_row(obj, key))
        else:
            rows.append(self.object_property_row( block, block['title']))
        
        if not rows:
            print(f"WARNING: No fields defined for '{block['title']}'")
            return

        df = pd.DataFrame.from_records(rows)
        df.set_index('Field', drop=True, inplace=True)
        md.push_table(df, class_='definitions')

    def render_md(self, schema_path, output_path):
        print(f"Processing schema '{schema_path}'")
        schema_path = Path(schema_path)

        with open(schema_path, 'r') as f:
            self.schema = json.load(f)

        self.schema['_key'] = '_root__'

        self.blocks = Queue()
        self.visited = set()

        md = MDWriter()

        md.push_comment(f"Don't modify this file directly.\nThis file was automatically generated from '{schema_path.name}'.")  # not implemented

        schema_name = schema_path.name.replace('.schema.json', '.json')
        md.push_heading(1, f"**`{schema_name}`** format definition")

        self.blocks.put(('object', self.schema))

        while not self.blocks.empty():
            typ, block = self.blocks.get()

            # if 'title' not in block:
            #     raise ValueError(f"Missing 'title' for field '{block['_key']}'")

            # if 'type' not in block:
            #     raise ValueError(f"Missing 'type' for field '{block['_key']}'")

            if block['title'] in self.visited:
                print(f"Skipping '{block['title']}' (already visited)")
                continue
            
            self.visited.add(block['title'])

            if typ == 'object':
                self.object_block(block, md)
            
            if typ == 'oneOf':
                self.oneOf_block(block, md)

        if output_path is None:
            return md.raw
        
        with open(output_path, 'w') as f:
            f.write(md.raw)
