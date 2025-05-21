from Tree import *
from lexer import Lexer
from tokens import *
from recovery import *


class Parser:
    def __init__(self, stream):
        self.stream = stream
        self.lexer = Lexer(stream)
        self.token: Token = eof
        self.next_token()
        return

    def next_token(self):
        """
        移动到下一个token
        """
        self.token = self.lexer.next()
        return

    def accept(self, token_kind: str):
        """
        检查当前token是否为指定类型，是则后移，不是就会报语法错误
        """
        if self.token.name == token_kind:
            prev_token = self.token
            self.next_token()
            return prev_token
        else:
            print(f"Syntax error: expected {token_kind}, but got {self.token.name}")
            return None

    """
    这是主方法，
    需要的功能就是，输入一段程序，无论其是否有错误，都要把它parse为一个语法树。
    对于错误结点，应该使用恢复机制确定右界，并以解析失败位置为左界，收集解析失败
    的子串，放入结点中，然后在右界继续编译过程。
    最后应该parse出一棵语法树，其中有正确结点和错误结点，然后我们对错误结点进行
    处理。先做到这一步好了。
    """

    def parse_compilation_unit(self):
        """
        CompilationUnit: [PackageDecl] ClassDecl*
        """
        try:
            pack_name = self.parse_package_declaration()
        except Exception as e:
            print(f"Error parsing package declaration: {e}")
            # TODO
        unit = CompilationUnit(pack_name, [])
        while self.token.name != "EOS":
            try:
                class_decl = self.parse_class_decl()
                unit.add_def(class_decl)
            except Exception as e:
                print(f"Error parsing class declaration: {e}")
                err_node = ClassDecl(0, "", [])
                err_node.is_normal_node = False

                # 进行错误恢复找右界
                err_tokens = recovery(self.lexer, RecoveryPolicy.find_toplevel_border)
                err_node.info = err_tokens
                unit.add_def(err_node)
        return unit

    def parse_class_decl(self):
        """
        ClassDecl: [Modifier] class ID [extends ID] { ClassMember* }
        """
        access = self.parse_modifier()

        self.accept("CLASS")
        class_name = self.parse_ident()

        extends = None
        if self.token.name == "EXTENDS":
            self.accept("EXTENDS")
            extends = self.parse_ident()

        self.accept("LBRACE")
        members = []
        while self.token.name != "RBRACE" and self.token.name != "EOS":
            member = None
            if self.is_method_declaration():
                member = self.parse_method_decl()
            else:
                member = self.parse_var_decl()
            members.append(member)
        self.accept("RBRACE")

        return ClassDecl(access, class_name, members, extends)

    def is_method_declaration(self):
        """
        判断是否是方法声明的辅助方法
        """
        saved_pos = self.lexer.ptr

        if self.token.name in ["PUBLIC", "PROTECTED", "PRIVATE"]:
            self.next_token()

        result = False
        if self.token.name == "VOID":
            result = True
        if self.token.name in ["INT", "BOOLEAN", "ID"]:
            self.next_token()
            if self.token.name == "ID":
                self.next_token()
                if self.token.name == "LPAREN":
                    result = True

        self.lexer.set_pos(saved_pos)
        self.next_token()
        return result

    def parse_expression(self):
        """
        Expression: ID = Expression | INT_LITERAL | BOOL_LITERAL
        """
        if self.token.name == "ID":
            ident = self.parse_ident()
            if self.token.name == "EQ":
                self.next_token()
                right = self.parse_expression()
                return Assignment(ident, right)
            return ident
        elif self.token.name == "INT_LITERAL":
            value = self.token.content
            self.next_token()
            return Literal("int", value)
        elif self.token.name in ["TRUE", "FALSE"]:
            value = self.token.name == "TRUE"
            self.next_token()
            return Literal("boolean", value)
        else:
            raise Exception(f"Unexpected token in expression: {self.token.name}")

    def parse_statement(self):
        """
        Statement: Block | IfStatement | VarDecl | Expression
        """
        try:
            if self.token.name == "LBRACE":
                return self.parse_block()
            elif self.token.name == "IF":
                return self.parse_if_statement()
            elif self.token.name in ["INT", "BOOLEAN"]:
                return self.parse_var_decl()
            else:
                return self.parse_expression()
        except Exception as e:
            print(f"Error parsing statement: {e}")

    def parse_if_statement(self):
        """
        IfStatement: if ( Expression ) Statement [else Statement]
        """
        self.accept("IF")
        self.accept("LPAREN")
        condition = self.parse_expression()
        self.accept("RPAREN")

        then_part = self.parse_statement()

        else_part = None
        if self.token.name == "ELSE":
            self.next_token()
            else_part = self.parse_statement()

        return IfStatement(condition, then_part, else_part)

    def parse_ident(self):
        if self.token.name == "ID":
            ident = Ident(self.token.content)
            self.next_token()
            return ident
        else:
            raise Exception("Expected ID")

    def parse_var_decl(self):
        """
        VarDecl: [Modifier] Type ID = Expression ;
        """
        try:
            access = self.parse_modifier()

            var_type = None
            if self.token.name in ["INT", "BOOLEAN"]:
                var_type = PrimitiveType(self.token.content)
                self.next_token()
            else:
                raise Exception(f"Expected type, got {self.token.name}")

            var_name = self.parse_ident()
            if not var_name:
                raise Exception("Expected variable name")

            initialization = None
            if self.token.name == "EQ":
                self.accept("EQ")
                initialization = self.parse_expression()

            self.accept("SEMI")
            return VarDecl(access, var_type, initialization)

        except Exception as e:
            print(f"Error in variable declaration: {str(e)}")
            # TODO

    def parse_param_list(self):
        """
        ParamList: (Type ID (COMMA Type ID)*)
        """
        params = []
        self.accept("LPAREN")

        if self.token.name == "RPAREN":
            self.accept("RPAREN")
            return params

        while True:
            param_type = None
            if self.token.name in ["INT", "BOOLEAN"]:
                param_type = PrimitiveType(self.token.content)
                self.next_token()
            else:
                break

            if self.token.name != "ID":
                break
            param_name = self.token.content
            self.next_token()

            params.append(VarDecl(0, param_type, None))

            if self.token.name != "COMMA":
                break
            self.accept("COMMA")

        self.accept("RPAREN")
        return params

    def parse_method_decl(self):
        """
        MethodDecl: [Modifier] Type ID (ParamList) (Block | SEMI)
        """
        access = self.parse_modifier()

        return_type = None
        if self.token.name == "VOID":
            return_type = PrimitiveType("void")
            self.next_token()
        elif self.token.name in ["INT", "BOOLEAN"]:
            return_type = PrimitiveType(self.token.content)
            self.next_token()
        else:
            raise Exception(f"Expected return type, got {self.token.name}")

        if self.token.name != "ID":
            raise Exception(f"Expected method name, got {self.token.name}")
        method_name = self.token.content
        self.next_token()

        params = self.parse_param_list()

        body = None
        if self.token.name == "LBRACE":
            body = self.parse_block()
        else:
            self.accept("SEMI")
            body = Block([])

        return MethodDecl(access, return_type, method_name, params, body)

    def parse_block(self):
        """
        Block: { Statement* }
        """
        statements = []

        self.accept("LBRACE")

        while self.token.name != "RBRACE" and self.token.name != "EOS":
            try:
                stmt = self.parse_statement()
                statements.append(stmt)
            except Exception as e:
                print(f"Error parsing statement: {str(e)}")
                error_node = Statement()
                error_node.is_normal_node = False

                error_tokens = recovery(
                    self.lexer, RecoveryPolicy.find_statement_border
                )
                error_node.info = error_tokens
                statements.append(error_node)

        self.accept("RBRACE")

        return Block(statements)

    def parse_modifier(self) -> int:
        match self.token.name:
            case "PUBLIC":
                self.accept("PUBLIC")
                return 3
            case "PROTECTED":
                self.accept("PROTECTED")
                return 2
            case "PRIVATE":
                self.accept("PRIVATE")
                return 1
            case _:
                return 0

    def parse_package_declaration(self) -> str:
        """
        PackageDecl: package ID ;
        """
        if self.token.name != "PACKAGE":
            return ""
        self.accept("PACKAGE")

        package_name = ""
        if self.token.name == "ID":
            package_name = self.token.content
            self.next_token()
        else:
            raise Exception("Expected ID after package keyword")

        self.accept("SEMI")
        return package_name
