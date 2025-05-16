# token is terminal
"""
直接用就行
"""
class Token:
    def __init__(self, name, content):
        self.name = name
        self.content = content
        return

    def get_content(self):
        if self.content is None:
            return "unknown " + self.name
        else:
            return str(self.content)

shared_str_to_terminal = {
    "package": Token("PACKAGE", "package"),
    "class": Token("CLASS", "class"),
    ";": Token("SEMI", ";"),
    "public": Token("PUBLIC", "public"),
    "protected": Token("PROTECTED", "protected"),
    "private": Token("PRIVATE", "private"),
    "{": Token("LBRACE", "{"),
    "}": Token("RBRACE", "}"),
    "=": Token("EQ", "="),
    "void": Token("VOID", "void"),
    "if": Token("IF", "if"),
    "(": Token("LPAREN", "("),
    ")": Token("RPAREN", ")"),
    "else": Token("ELSE", "else"),
    "true": Token("TRUE", "true"),
    "false": Token("FALSE", "false"),
    "int": Token("INT", "int"),
    "boolean": Token("BOOLEAN", "boolean"),
    "end_of_stream": Token("EOS", "end_of_stream")
}

test_terminal_id = Token("ID", "name")
test_terminal_int_literal = Token("INT_LITERAL", "123")
test_terminal_bool_literal = Token("BOOL_LITERAL", "true")
# like any error tokens
test_terminal_illegal_token = Token("ERROR", "error_token")
eof = shared_str_to_terminal["end_of_stream"]
