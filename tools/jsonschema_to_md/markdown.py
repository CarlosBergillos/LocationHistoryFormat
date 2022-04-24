from copy import copy

from tabulate import tabulate


class MDElement:
    INDENT = "\t"

    def __init__(self):
        self.indents = 0

    @property
    def md(self):
        return ""

    def unindent(self):
        new = copy(self)
        new.indents -= 1
        return new

    def indent(self):
        new = copy(self)
        new.indents += 1
        return new


class MDHeading(MDElement):
    def __init__(self, level, text):
        assert level <= 6
        self.level = level
        self.text = text

    @property
    def md(self):
        return f"{'#' * self.level} {self.text}\n\n"


class MDParagraph(MDElement):
    def __init__(self, text, indents=0):
        self.text = text
        self.indents = indents

    @property
    def md(self):
        ind = self.INDENT * self.indents
        return ind + self.text.replace("\n", "\n" + ind) + "\n\n"


class MDCodeBlock(MDElement):
    def __init__(self, text, language=None, title=None, indents=0):
        self.text = text
        self.language = language
        self.title = title
        self.indents = indents

    @property
    def md(self):
        ind = self.INDENT * self.indents
        text = ind + self.text.replace("\n", "\n" + ind)
        return f"{ind}```{self.language or ''} title=\"{self.title or ''}\"\n{text}\n{ind}```\n\n"


class MDComment(MDElement):
    def __init__(self, text):
        self.text = text

    @property
    def md(self):
        return f"<!---\n{self.text}\n-->\n\n"


class MDTable(MDElement):
    def __init__(self, rows, class_=None):
        self.rows = rows
        self.class_ = class_

    @property
    def md(self):
        def clean_value(v):
            if v is None:
                return ""

            # v = v.replace('\n', '<br>')
            v = v.replace("\n", '<p style="margin: 10px 0;"></p>')

            return v

        raw = ""

        rows = [{k: clean_value(v) for k, v in row.items()} for row in self.rows]

        if self.class_ is not None:
            raw += f'<div class="{self.class_}"></div>\n\n'  # note we cannot add a class to the table, we create a separate 'sentinel' div.

        raw += tabulate(rows, headers="keys", showindex=False, tablefmt="pipe")
        raw += f"\n\n"

        return raw


class MDWriter:
    def __init__(self):
        self.raw = ""

    def push_heading(self, level, text):
        heading = MDHeading(level, text)
        self.raw += heading.md

    def push_paragraph(self, text):
        paragraph = MDParagraph(text)
        self.raw += paragraph.md

    def push_codeblock(self, text, language=None, title=None):
        codeblock = MDCodeBlock(text=text, language=language, title=None)
        self.raw += codeblock.md

    def push_comment(self, text):
        comment = MDComment(text)
        self.raw += comment.md

    def push_table(self, rows, class_=None):
        table = MDTable(rows, class_)
        self.raw += table.md

    def push_admonition(self, content, type="info", title="", collapsible=False, start_expanded=False):
        if isinstance(content, str):
            text = MDParagraph(content).indent().md
        elif isinstance(content, MDElement):
            text = content.indent().md
        else:
            raise NotImplementedError(())

        if collapsible:
            if start_expanded:
                start = "???+"
            else:
                start = "???"
        else:
            start = "!!!"

        self.raw += f'{start} {type} "{title}"\n\n{text}\n\n'
