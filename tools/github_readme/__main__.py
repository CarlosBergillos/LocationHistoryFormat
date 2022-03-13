import re

MAIN_INDEX_PATH  ="./docs/index.md"
GITHUB_README_PATH = "./README.md"
BASE_URL = "https://www.locationhistoryformat.com/"
DISCLAIMER_HEADER = f"<!-- NOTE: Don't modify README.md file directly. Modify {MAIN_INDEX_PATH} instead and it will be reflected in README.md after build. -->"


def main():
    with open(MAIN_INDEX_PATH, 'r') as inp, open(GITHUB_README_PATH, 'w') as out:
        out.write(DISCLAIMER_HEADER + "\n\n")
        for line in inp.readlines():
            # remove images
            line = re.sub(r"!\[.*\]\(.*\)", "", line) 

            # adapt local URLs
            line = re.sub(r"\./([0-9A-Za-z/]+)\.md", rf"{BASE_URL}\1", line)

            out.write(line)


if __name__ == "__main__":
    main()
