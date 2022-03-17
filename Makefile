STATIC_SCHEMAS_DIR = ./docs/schemas/
SOURCES_DIR = ./schemas/
EXPORTS_DIR = ./docs/reference/

SOURCES = \
	settings:=Settings.schema.json \
	records:=Records.schema.json

TOOL_JSONSCHEMA2MD = $(wildcard ./tools/jsonschema_to_md/*.py)
TOOL_GITHUBREADME = $(wildcard ./tools/github_readme/*.py)

SOURCES_NAMES = $(foreach x,$(SOURCES),$(lastword $(subst :=, ,$x)))
EXPORT_NAMES = $(foreach x,$(SOURCES),$(firstword $(subst :=, ,$x)))
$(foreach x,$(SOURCES),$(eval SRC_$x))  # define SRC_* global variables

EXPORTED_DOCS := $(addsuffix .md,$(EXPORT_NAMES))
EXPORTED_DOCS := $(addprefix $(EXPORTS_DIR),$(EXPORTED_DOCS))
SOURCES_FILES := $(addprefix $(SOURCES_DIR),$(SOURCES_NAMES))
STATIC_SCHEMAS_FILES := $(addprefix $(STATIC_SCHEMAS_DIR),$(SOURCES_NAMES))

.PHONY: build deploy clean jsonschema2md staticschemas

.SECONDEXPANSION:
$(EXPORTS_DIR)%.md: $(SOURCES_DIR)$$(SRC_%) $(TOOL_JSONSCHEMA2MD)
	python -m tools.jsonschema_to_md $< -o $@

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
