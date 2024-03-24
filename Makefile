STATIC_SCHEMAS_DIR = ./docs/schemas/
SOURCES_DIR = ./schemas/
EXPORTS_DIR = ./docs/reference/

# List of source schemas to include, each item in the form:
# {output_key}:={input_file}
SOURCES = \
	settings:=Settings.schema.json \
	records:=Records.schema.json \
	semantic:=Semantic.schema.json \
	timeline-edits:=TimelineEdits.schema.json

# List of titles to use in the output MD files, each item in the form:
# {output_key}:={output_title}
# Note that '\_' is replaced with a whitespace, and that backticks '`' need to be escaped with '\`'.
SOURCE_TITLES = \
	settings:=**\`Settings.json\`**\_Format\_Definition \
	records:=**\`Records.json\`**\_Format\_Definition \
	semantic:=Semantic\_Location\_History\_Format\_Definition \
	timeline-edits:=Timeline\_Edits\_Format\_Definition


TOOL_JSONSCHEMA2MD = $(wildcard ./tools/jsonschema_to_md/*.py) $(wildcard ./tools/jsonschema_to_md/templates/*.jinja)
TOOL_GITHUBREADME = $(wildcard ./tools/github_readme/*.py)

SOURCES_NAMES = $(foreach x,$(SOURCES),$(lastword $(subst :=, ,$x)))
EXPORT_NAMES = $(foreach x,$(SOURCES),$(firstword $(subst :=, ,$x)))
$(foreach x,$(SOURCES),$(eval SRC_$x))  # define SRC_* global variables
$(foreach x,$(SOURCE_TITLES),$(eval SRCTITLE_$(subst \_, ,$x)))  # define SRCTITLE_* global variables

EXPORTED_DOCS := $(addsuffix .md,$(EXPORT_NAMES))
EXPORTED_DOCS := $(addprefix $(EXPORTS_DIR),$(EXPORTED_DOCS))
SOURCES_FILES := $(addprefix $(SOURCES_DIR),$(SOURCES_NAMES))
STATIC_SCHEMAS_FILES := $(addprefix $(STATIC_SCHEMAS_DIR),$(SOURCES_NAMES))

.PHONY: build deploy clean jsonschema2md staticschemas

.SECONDEXPANSION:
$(EXPORTS_DIR)%.md: $(SOURCES_DIR)$$(SRC_%) $(TOOL_JSONSCHEMA2MD)
	python -m tools.jsonschema_to_md $< -o $@ -t "$(SRCTITLE_$*)"

$(STATIC_SCHEMAS_DIR):
	mkdir -p $(STATIC_SCHEMAS_DIR)

$(STATIC_SCHEMAS_DIR)%: $(SOURCES_DIR)%
	cp $< $@

README.md: ./docs/index.md $(TOOL_GITHUBREADME)
	python -m tools.github_readme

jsonschema2md: $(EXPORTED_DOCS)

staticschemas: $(STATIC_SCHEMAS_DIR) | $(STATIC_SCHEMAS_FILES)

build: jsonschema2md README.md

deploy: jsonschema2md README.md staticschemas

clean:
	rm $(EXPORTED_DOCS) -f
	rm $(STATIC_SCHEMAS_FILES) -f
