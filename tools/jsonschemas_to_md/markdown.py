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
    
    def push_table(self, rows, class_=None):
        def clean_value(v):
            if v is None:
                return ''
            
            # v = v.replace('\n', '<br>')
            v = v.replace('\n', '<p style="margin: 10px 0;"></p>')
        
            return v

        rows = [{k: clean_value(v) for k, v in row.items()} for row in rows]

        if class_ is not None:
            self.raw +=f"<div class=\"{class_}\"></div>\n\n"  # note we cannot add a class to the table, we create a separate 'sentinel' div.

        self.raw += tabulate(rows, headers="keys", showindex=False, tablefmt="pipe")
        self.raw += f"\n\n"
    
    def push_admonition(self, text, type="info", title=""):
        self.raw += f"!!! {type} \"{title}\"\n\n\t{text}\n\n"
