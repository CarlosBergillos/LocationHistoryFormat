import json


class Empty:
    def __getattr__(self, _):
        return None


class JSONSchema:
    def __init__(self, raw_schema, key=None, path='#', root_schema=None):
        self.raw_schema = raw_schema
        self.key = key
        self.path = path
        self.primary_path = path
        self.root_schema = root_schema or self
        self.refd_schema = Empty()
        self.item_schema = Empty()

        if self.ref is not None:
            self.refd_schema = self.get(self.ref)
            self.primary_path = self.ref
        
        if self.type == 'array':
            if 'items' not in self.raw_schema:
                raise ValueError("Type 'array' in schema must have an 'items' object.")

            self.item_schema = self.get(self.path + '/items')

    @property
    def type(self):
        return self.raw_schema.get('type') or self.refd_schema.type
    
    @property
    def format(self):
        return self.raw_schema.get('format') or self.refd_schema.format

    @property
    def title(self):
        return self.raw_schema.get('title') or self.refd_schema.title

    @property
    def description(self):
        return self.raw_schema.get('description') or self.refd_schema.description
    
    @property
    def examples(self):
        return self.raw_schema.get('examples') or self.refd_schema.example or []
    
    @property
    def example(self):
        if not self.examples:
            return None

        example = self.examples[0]

        if isinstance(example, dict):
            return json.dumps(example, indent=4)

        return json.dumps(example)
    
    @property
    def oneOf(self):
        return self.raw_schema.get('oneOf') or self.refd_schema.oneOf

    @property
    def ref(self):
        return self.raw_schema.get('$ref') or self.refd_schema.ref
    
    @property
    def raw_properties(self):
        return self.raw_schema.get('properties') or self.refd_schema.raw_properties or {}
    
    @property
    def properties_keys(self):
        return sorted(self.raw_properties.keys())

    @property
    def properties_schemas(self):
        try:
            return [self.get(self.path + '/properties/' + key) for key in self.properties_keys]
        except ValueError:
            return [self.get(self.refd_schema.path + '/properties/' + key) for key in self.properties_keys]
    
    def get(self, path):
        base, path_ = path.split('#')
        parts = path_.split('/')
        
        raw_schema = self.root_schema.raw_schema
        for part in parts:
            if not part:
                continue

            raw_schema = raw_schema.get(part)

            if raw_schema is None:
                raise ValueError(f"Did not find '{path}' in schema.")

        key = path.split('/')[-1]

        return JSONSchema(raw_schema, key, path, root_schema=self.root_schema)
