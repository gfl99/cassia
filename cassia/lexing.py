from prompt_toolkit.lexers import Lexer
from prompt_toolkit.styles import Style


class SelectActionLexer(Lexer):
    def lex_document(self, document):
        lines = document.lines
        def get_line(i):
            text = lines[i]
            words = text.split()
            has_time = False
            if words and len(words[0])==4 and all(c.isdigit() for c in words[0]) and len(words[0]):
                has_time = True
            elif words and len(words[0])==5 and all(c.isdigit() for c in words[0][:2]+words[0][3:]):
                has_time = True

            actions = {'D': 'delete', 'L': 'list', 'X': 'exit', 'R': 'reports', 'P': 'print', 'q': 'exit',
                       'd': 'delete', 'l': 'list', 'x': 'exit', 'r': 'reports', 'p': 'print', 'Q': 'exit',
                       'delete': 'delete', 'list': 'list', 'exit': 'exit', 'reports': 'reports', 'print': 'print', 'quit': 'exit',
                       'Delete': 'delete', 'List': 'list', 'Exit': 'exit', 'Reports': 'reports', 'Print': 'print', 'Quit': 'exit',}
            if action := actions.get(text):
                return [(f"class:action-{action}", text)]
            elif has_time:
                return [("class:time", words[0])] + [("class:description", text[len(words[0]):])]
            elif len(words)==1:
                return [("class:text", text)]
            else:
                return [("class:invalid", text)]
        return get_line


select_action_style = Style([
    ('time', '#ff0000 bold underline'),
    ('action-reports', 'purple bold underline'),
    ('action-delete',  'red bold underline'),
    ('action-list',    'blue bold underline'),
    ('action-print',   'purple bold underline'),
    ('action-exit',    'green bold underline'),
    ('description', 'italic'),
    ('invalid', 'gray'),
])