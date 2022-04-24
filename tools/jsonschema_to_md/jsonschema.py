import json
from pathlib import Path

from json_source_map import calculate


class Empty:
    def __getattr__(self, _):
        return None

    def __bool__(self):
        return False


class JSONSchema:
    def __init__(self, raw_schema, key=None, path="#", root_schema=None, file_path=None, source_map=None):
        self.raw_schema = raw_schema
        self.key = key
        self.path = path
        self.primary_path = path
        self.root_schema = root_schema or self
        self.refd_schema = Empty()
        self.item_schema = Empty()
        self.file_path = Path(file_path) if file_path is not None else self.root_schema.file_path
        self.file_name = self.file_path.name
        self.source_map = source_map
        self.file_line_start = self.root_schema.source_map.get(self.path[1:]).value_start.line + 1
        self.file_line_end = self.root_schema.source_map.get(self.path[1:]).value_end.line + 1

        if self.ref is not None:
            self.refd_schema = self.get(self.ref)
            self.primary_path = self.ref

        if self.type == "array":
            try:
                self.item_schema = self.get(self.primary_path + "/items")
            except ValueError:
                self.item_schema = Empty()

    @classmethod
    def from_file(cls, file_path):
        with open(file_path, "r") as f:
            raw_text = f.read()
            f.seek(0)
            raw_schema = json.load(f)

        schema = cls(raw_schema, file_path=file_path, source_map=calculate(raw_text))

        return schema

    @property
    def type(self):
        return self.raw_schema.get("type", self.refd_schema.type)

    @property
    def format(self):
        return self.raw_schema.get("format", self.refd_schema.format)

    @property
    def title(self):
        return self.raw_schema.get("title", self.refd_schema.title)

    @property
    def description(self):
        return self.raw_schema.get("description", self.refd_schema.description)

    @property
    def examples(self):
        return self.raw_schema.get("examples", self.refd_schema.examples or [])

    @property
    def example(self):
        if not self.examples:
            return None

        return self.examples[0]

    @property
    def oneOf(self):
        oneOf = self.raw_schema.get("oneOf", self.refd_schema.oneOf)

        if oneOf is None:
            return None

        return [self.get(self.primary_path + "/oneOf/" + str(i)) for i in range(len(oneOf))]

    @property
    def const(self):
        return self.raw_schema.get("const", self.refd_schema.const)

    @property
    def ref(self):
        return self.raw_schema.get("$ref", self.refd_schema.ref)

    @property
    def raw_properties(self):
        return self.raw_schema.get("properties", self.refd_schema.raw_properties or {})

    @property
    def properties_keys(self):
        return sorted(self.raw_properties.keys())

    @property
    def properties_schemas(self):
        return [self.get(self.primary_path + "/properties/" + key) for key in self.properties_keys]

    def get(self, path):
        try:
            base, path_ = path.split("#")
        except:
            raise ValueError(f"Could not split by '#' path '{path}'.")

        parts = path_.split("/")

        raw_schema = self.root_schema.raw_schema
        for part in parts:
            if not part:
                continue

            if isinstance(raw_schema, dict):
                raw_schema = raw_schema.get(part)
            elif isinstance(raw_schema, list):
                try:
                    idx = int(part)
                except ValueError:
                    raise ValueError(f"Path '{path}' encountered an array but part is not an integer.")

                try:
                    raw_schema = raw_schema[idx]
                except ValueError:
                    raise ValueError(f"Index {idx} out of range in path '{path}'.")

            if raw_schema is None:
                raise ValueError(f"Did not find '{path}' in schema.")

        key = path.split("/")[-1]

        return JSONSchema(raw_schema, key, path, root_schema=self.root_schema)
