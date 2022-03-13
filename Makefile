SOURCES_DIR = ./schemas/
EXPORTS_DIR = ./docs/reference/

SOURCES = \
	settings:=Settings.schema.json \
	records:=Records.schema.json

TOOL_JSONSCHEMA2MD = $(wildcard ./tools/jsonschemas_to_md/*.py)


EXPORT_NAMES = $(foreach x,$(SOURCES),$(firstword $(subst :=, ,$x)))
$(foreach x,$(SOURCES),$(eval SRC_$x))  # define SRC_* global variables

EXPORTED_DOCS := $(addsuffix .md,$(EXPORT_NAMES))
EXPORTED_DOCS := $(addprefix $(EXPORTS_DIR),$(EXPORTED_DOCS))

.PHONY: all clean jsonschema2md

.SECONDEXPANSION:
$(EXPORTS_DIR)%.md: $(SOURCES_DIR)$$(SRC_%) $(TOOL_JSONSCHEMA2MD)
	python -m tools.jsonschemas_to_md $< -o $@

jsonschema2md: $(EXPORTED_DOCS)

all: jsonschema2md

clean:
	rm $(EXPORTED_DOCS) -f
