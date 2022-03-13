# Location History Format

Unofficial and collaborative format definition and documentation for Google Location History files.

![Example of Location History data on a map.](./static/hero.png)

Google (through its [Takeout service][Google Takeout]) allows users to easily and conveniently download their Location History data.
Unfortunately Google has not provided proper official documentation for these files, so it can sometimes be difficult to navigate the structure of the files and understand the meaning of its fields.
This project attempts to fill that gap and do the job that Google should have done.


## Goals

The goals of this project are two-fold:

- **Provide a standarized format definition/specification describing the format and structure of the files.**
These format definitions are given in the form of [JSON schemas], which can be used, for example, for automatic validation of JSON files and to aid in the development of parsers.
These files can be found in the [schemas folder][Schemas] in the repository.

- **Provide accessible and user-friendly documentation for these formats.** *TODO* how to interpret and what to expect from these files and its contents ([locationhistoryformat.com][Homepage]).


## Disclaimer

This project is not affiliated, endorsed by, or in any way officially connected with Google.
Official support for Google products can be found at <https://support.google.com/>.

An effort is being made to keep the information provided by this project accurate and up-to-date,
but due to its nature, the information provided might be inaccurate and/or out-of-date.
Google has repeatedly made modifications to the format throughout the years without prior warning.


## Contributing

Contributions are welcome!
If you notice errors, out-of-date information, or missing information, you can help improve it, see [Contributing].


## License

This project is licensed under the terms of the [MIT License][License].


[Homepage]: {{ config.site_url }}
[Google Takeout]: https://takeout.google.com/settings/takeout
[JSON schemas]: https://json-schema.org
[Schemas]: {{ config.repo_url }}/tree/main/schemas
[Contributing]: ./contributing.md
[License]: {{ config.repo_url }}/blob/main/LICENSE
