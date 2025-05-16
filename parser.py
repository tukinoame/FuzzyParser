from Tree import *
from lexer import Lexer
from tokens import *

class Parser:
    def __init__(self, stream):
        self.stream = stream
        self.lexer = Lexer(stream)
        self.token: Token = eof
        self.next_token()
        return

    """
    移动到下一个token
    """
    def next_token(self):
        self.token = self.lexer.next()
        return

    """
    检查当前token是否为指定类型，是则后移，不是就会报语法错误
    """
    def accept(self, token_kind: str):
        if self.token.name == token_kind:
            self.next_token()
        else:
            pass   # TODO

    """
    这是主方法，
    需要的功能就是，输入一段程序，无论其是否有错误，都要把它parse为一个语法树。
    对于错误结点，应该使用恢复机制确定右界，并以解析失败位置为左界，收集解析失败
    的子串，放入结点中，然后在右界继续编译过程。
    最后应该parse出一棵语法树，其中有正确结点和错误结点，然后我们对错误结点进行
    处理。先做到这一步好了。
    """
    def parse_compilation_unit(self):
        pass   # TODO

    def parse_class_decl(self):
        pass

    def parse_expression(self):
        pass

    def parse_statement(self):
        pass

    def parse_ident(self):
        pass

    def parse_var_decl(self):
        pass

    def parse_method_decl(self):
        pass

    def parse_block(self):
        pass

    def parse_modifier(self) -> int:
        pass

    def parse_package_declaration(self) -> str:
        pass
