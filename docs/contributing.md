# Contributing

Open collaboration is fundamental for this project, a single person can't encounter and document all edge cases of the files.
Moreover, the format is constantly changing, so updates will frequently be needed.

Versioning difficulties:

- There is no known versioning system or version clues for the file format,
so it is difficult to spot and accurately document when changes to the format happen.
- Changes to the exported data is usually not rolled out at the same time for all Google users

- Sensitive data.

These facts makes formalizing and keeping track of changes a difficult and unique challenge.

Due to the Sensitive information, proof is not required, and it would be useless anyway. So good faith and 'rigurosity' is expected from contributors.


<!-- ## How to Contribute

All source code, documentation files, and schemas can be found on the [GitHub repository][Repo].

Help can be divided into two main groups: -->


## Improving the JSON Schemas

All JSON schemas can be found in the [`schemas/`][schemas/] folder of the repository.
Pull requests are welcome.
Ideally contributors should be familiar with the structure of JSON Schema files.

All documented objects and properties should at least have the following fields:

- `title`:
In most cases it is just a "humanized" version of the key.

- `type`:
One of `"object"`, `"array"`, `"string"`, `"number"`, `"boolean"`, `"null"`.

- `description`:
Can make use of common basic Markdown syntax.
It can be an empty string if no information is known (in which case a `helpWanted` field should be present).

It addition to other basic JSON Schema fields, the following non-standard fields are also supported:

- `added`:
Estimated date that this object/property was added to the format.
Example value: `"around January 2022"`.

- `removed`:
Estimated date that this object/property was removed from the format.
Example value: `"around January 2022"`.

- `helpWanted`:
Short description to inform that the information provided for this object/property is incomplete and help from the community is welcome.
Example value: `"The meaning of this field is uncertain. Are other values possible?"`

To convert the schema files to Markdown files (which are then used for the documentation site)
a custom Python script is used (see [`tools/jsonschema_to_md/`][tools/jsonschema_to_md/]).

!!! info

    Not all standard JSON Schema language features are supported when building the site, (and there is no intention on supporting all),
    only support for those required has been added.
    If you miss some JSON Schema feature in the Markdown generator [create a new issue][Issues] or a pull request.

## Improving the Guides

To improve the documentation guides provided in this site modify the Markdown files found in the [`docs/guides/`][docs/guides/] folder and submit a pull request.
Most common Markdown syntax can be used in the files, plus additional syntax extensions provided by the [Material for MkDocs] theme.


## Testing Locally

In order to set-up a local environment to preview and test changes to the site first clone the [GitHub repository][Repo], then:

To install all requirements run:

```
pip install -r requirements.txt
```

To transform the JSON schemas in the `schemas/` folder to Markdown files run:

```
make build
```

!!! info
    
    The generated Markdown files are stored in the `/docs/reference` folder.
    Note that these dynamically generated Markdown files should not be included in the repository.

To start a local web server and view the site run:

```
mkdocs serve
```


## Reporting an Issue

[Repo]: {{ config.repo_url }}
[Issues]: {{ config.repo_url }}/issues
[schemas/]: {{ config.repo_url }}/tree/main/schemas
[docs/guides/]: {{ config.repo_url }}/tree/main/docs/guides
[docs/reference/]: {{ config.repo_url }}/tree/main/docs/reference
[tools/jsonschema_to_md/]: {{ config.repo_url }}/tree/main/tools/jsonschema_to_md
[Material for MkDocs]: https://squidfunk.github.io/mkdocs-material/
