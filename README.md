<!-- NOTE: Don't modify README.md file directly. Modify ./docs/index.md instead and it will be reflected in README.md after build. -->

# Location History Format

Unofficial and collaborative format definition and documentation for Google Location History files.


Google (through its [Takeout service][Google Takeout]) allows users to easily and conveniently download their Location History data.
Unfortunately Google has not provided proper official documentation for these files, so it can sometimes be difficult to navigate the structure of the files and understand the meaning of its fields.
This project attempts to fill that gap and do the job that Google should have done.


## Goals

The goals of this project are two-fold:

- **Provide a standardized format definition describing the structure and contents of the files.**
These format definitions are given in the form of [JSON schemas], which can be used, for example, for automatic validation of JSON files and to aid in the development of parsers.
These files can be found in the [schemas folder][Schemas] in the repository.

- **Provide accessible and user-friendly documentation for these formats.**
The documentation is presented in a public site ([locationhistoryformat.com][Homepage]) which provides basic guides and reference pages detailing the structure and fields of the files.
The reference pages are automatically built from the JSON schemas, presenting the information in a much more readable way.


## Disclaimer

This project is not affiliated, endorsed by, or in any way officially connected with Google.
Official support for Google products can be found at <https://support.google.com/>.

An effort is being made to keep the information provided by this project accurate and up-to-date,
but due to its nature, the information provided might be inaccurate and/or out-of-date.
Google has repeatedly made modifications to the format throughout the years without prior warning.


## Contributing

Contributions are welcome!
If you notice errors, out-of-date information, or missing information, you can help improve it.
See [Contributing].


## License

This project is licensed under the terms of the [MIT License][License].


[Homepage]: https://locationhistoryformat.com
[Google Takeout]: https://takeout.google.com/settings/takeout
[JSON schemas]: https://json-schema.org
[Schemas]: https://github.com/CarlosBergillos/LocationHistoryFormat/tree/main/schemas
[Contributing]: https://www.locationhistoryformat.com/contributing
[License]: https://github.com/CarlosBergillos/LocationHistoryFormat/blob/main/LICENSE
