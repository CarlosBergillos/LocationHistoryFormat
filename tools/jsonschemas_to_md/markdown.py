from tabulate import tabulate


class MDWriter:
    def __init__(self):
        self.raw = ''
    
    def push_heading(self, level, text):
        assert level <= 6
        self.raw += f"{'#' * level} {text}\n\n"

    def push_paragraph(self, text, indent=False, block=False):
        if not text:
            text = '-'

        if indent:
            if block:
                text = text.replace('\n', '\n\t> ')
                text = text.replace('> \t<', '\t')  # admonition contents should not have '>', so we have flagged them with '<'.
                self.raw += f":\t> {text}\n\n"
            else:
                text = text.replace('\n', '\n\t')
                self.raw += f":\t{text}\n\n"
        else:
            self.raw += f"{text}\n\n"
    
    def push_comment(self, text):
        self.raw += f"<!---\n{text}\n-->\n\n"
    
    def push_table(self, table, class_=None):
        # table = table.applymap(lambda x: x.replace('\n', '<br>'))
        table.replace({None: ''}, inplace=True)
        table = table.applymap(lambda x: x.replace('\n', '<p style="margin: 10px 0;"></p>'))

        if class_ is not None:
            self.raw +=f"<div class=\"{class_}\"></div>\n\n"  # note we cannot add a class to the table, we create a separate 'sentinel' div.

        self.raw += tabulate(table, headers="keys", showindex=True, tablefmt="pipe")
        self.raw += f"\n\n"
    
    def push_admonition(self, text, type="info", title=""):
        self.raw += f"!!! {type} \"{title}\"\n\n\t{text}\n\n"
