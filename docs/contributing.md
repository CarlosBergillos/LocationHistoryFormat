# Contributing

Open collaboration is fundamental for this project, a single person can't encounter and document all edge cases of the files.
Additionally, Google periodically updates the format and structure of the files without prior warning,
so updates to the format definitions will also be needed periodically but might be easy to miss.

All source code, documentation files, and schemas can be found in the project's [GitHub repository][Repo].
If you notice incorrect, out-of-date, or missing information, you can help by [creating a new issue][Issues] or [creating a pull request][Pull Requests].

Note that Google's Location History data presents unique challenges that make spotting, formalizing, and accurately keeping track of the changes to the format significantly difficult.
In particular, there is no known versioning system for the file format (or other indirect versioning clues),
and changes to the format of the extracted files are usually not rolled out at the same time for all Google users.


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

In addition to other basic JSON Schema fields, the following non-standard fields are also supported:

- `added`:
Estimated approximate date that this object/property was added to the format.
Example: `"around January 2022"`.

- `removed`:
Estimated approximate date that this object/property was removed from the format.
Example: `"around January 2022"`.

- `helpWanted`:
Short description to inform that the information provided for this object/property is incomplete and help from the community is welcome.
Example: `"The meaning of this field is uncertain. Are other values possible?"`

To convert the JSON Schema files to Markdown files (which are then used for the documentation site)
a custom Python script is used (see [`tools/jsonschema_to_md/`][tools/jsonschema_to_md/]).

!!! info

    Not all standard JSON Schema language features are supported when building the site
    (and it is not in the scope of this project to build a complete JSON Schema to Markdown generator).
    If you miss some JSON Schema feature in the Markdown generator [create a new issue][Issues] or a pull request.


## Improving the Guides

To improve the documentation guides provided in this site modify the Markdown files found in the [`docs/guides/`][docs/guides/] folder and submit a pull request.
Most common Markdown syntax is supported, plus additional syntax extensions provided by the [Material for MkDocs] theme.


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


[Repo]: {{ config.repo_url }}
[Issues]: {{ config.repo_url }}/issues
[Pull Requests]: {{ config.repo_url }}/pulls
[schemas/]: {{ config.repo_url }}/tree/main/schemas
[docs/guides/]: {{ config.repo_url }}/tree/main/docs/guides
[docs/reference/]: {{ config.repo_url }}/tree/main/docs/reference
[tools/jsonschema_to_md/]: {{ config.repo_url }}/tree/main/tools/jsonschema_to_md
[Material for MkDocs]: https://squidfunk.github.io/mkdocs-material/
