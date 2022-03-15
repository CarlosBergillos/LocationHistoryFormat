"""This script creates a new README.md file in the root folder of the project
by copying the contents of the file at docs/index.md, while applying some
transformations to the contents of the file to adapt it to work well on GitHub.
"""

import re

from ..common import repo_url, site_url

MAIN_INDEX_PATH = "./docs/index.md"
GITHUB_README_PATH = "./README.md"
BASE_URL = "https://www.locationhistoryformat.com/"
DISCLAIMER_HEADER = f"<!-- NOTE: Don't modify README.md file directly. Modify {MAIN_INDEX_PATH} instead and it will be reflected in README.md after build. -->"


def main():
    config_maps = {
        "config.site_url": site_url(),
        "config.repo_url": repo_url(),
    }

    with open(MAIN_INDEX_PATH, "r") as inp, open(GITHUB_README_PATH, "w") as out:
        out.write(DISCLAIMER_HEADER + "\n\n")
        lines = iter(inp.readlines())
        for original_line in lines:
            line = original_line

            # remove images
            line = re.sub(r"!\[.*\]\(.*\)", "", line)

            # adapt local URLs
            line = re.sub(r"\./([0-9A-Za-z/_]+)\.md", rf"{BASE_URL}\1", line)

            # replace config macros
            line = re.sub(r"{{ ([0-9A-Za-z._]+) }}", lambda match: config_maps[match.group(1)], line)

            # adapt admonitions
            if line.startswith("!!!"):
                # NOTE: we are assuming admonitions never have images or local URLs

                for line in lines:
                    if line == "\n":
                        out.write("\n")
                    elif line.startswith(4 * " "):
                        out.write("> " + line[4:])
                    else:
                        break

            if original_line == line or line != "\n":
                out.write(line)


if __name__ == "__main__":
    main()
