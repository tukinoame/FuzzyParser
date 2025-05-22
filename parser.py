from pytest import Package
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
            pack = self.parse_package_declaration()
        except SyntaxError as e:
            print(f"Error parsing package declaration: {e}")
            erre_node = PackageDecl("")
            erre_node.is_normal_node = False
            err_tokens = recovery(self.lexer, RecoveryPolicy.find_toplevel_border)
            erre_node.info = err_tokens
            pack = erre_node

        unit = CompilationUnit(pack, [])
        while self.token.name != "EOS":
            try:
                class_decl = self.parse_class_decl()
                unit.add_def(class_decl)
            except SyntaxError as e:
                print(f"Error parsing class declaration: {e}")
                err_node = ClassDecl(0, "", [])
                err_node.is_normal_node = False
                err_tokens = recovery(self.lexer, RecoveryPolicy.find_toplevel_border)
                err_node.info = err_tokens
                unit.add_def(err_node)
        return unit

    def parse_class_decl(self):
        """
        ClassDecl: [Modifier] class ID [extends ID] { ClassMember* }
        """
        access = self.parse_modifier()

        claz = self.accept("CLASS")
        if not claz:
            raise SyntaxError(
                "Expected 'class' keyword", shared_str_to_terminal["class"]
            )
        class_name = self.parse_ident()
        if not class_name:
            raise SyntaxError("Expected class name", test_terminal_id)

        extends = None
        if self.token.name == "EXTENDS":
            self.accept("EXTENDS")
            extends = self.parse_ident()
            if not extends:
                raise SyntaxError(
                    "Expected class name after 'extends'", test_terminal_id
                )

        lbrace = self.accept("LBRACE")
        if not lbrace:
            raise SyntaxError(
                "Expected '{' after class declaration", shared_str_to_terminal["{"]
            )

        members = []
        while self.token.name != "RBRACE" and self.token.name != "EOS":
            member = None
            if self.is_method_declaration():
                try:
                    member = self.parse_method_decl()
                except SyntaxError as e:
                    print(f"Error parsing method declaration: {e}")
                    err_node = MethodDecl(0, PrimitiveType("void"), "", [], Block([]))
                    err_node.is_normal_node = False
                    err_tokens = recovery(
                        self.lexer, RecoveryPolicy.find_class_member_border
                    )
                    err_node.info = err_tokens
                    member = err_node
            else:
                try:
                    member = self.parse_var_decl()
                except SyntaxError as e:
                    print(f"Error parsing variable declaration: {e}")
                    err_node = VarDecl(0, PrimitiveType("int"), None)
                    err_node.is_normal_node = False
                    err_tokens = recovery(
                        self.lexer, RecoveryPolicy.find_class_member_border
                    )
                    err_node.info = err_tokens
                    member = err_node
            members.append(member)

        rbrace = self.accept("RBRACE")
        if not rbrace:
            raise SyntaxError(
                "Expected '}' at the end of class declaration",
                shared_str_to_terminal["}"],
            )

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
        if self.token.name == "LBRACE":
            try:
                blk = self.parse_block()
                return blk
            except SyntaxError as e:
                print(f"Error parsing block: {e}")
                error_node = Block([])
                error_node.is_normal_node = False

                error_tokens = recovery(
                    self.lexer, RecoveryPolicy.find_statement_border
                )
                error_node.info = error_tokens
                return error_node
        elif self.token.name == "IF":
            try:
                ifstmt = self.parse_if_statement()
                return ifstmt
            except SyntaxError as e:
                print(f"Error parsing if statement: {e}")
                error_node = IfStatement(None, None, None)
                error_node.is_normal_node = False

                error_tokens = recovery(
                    self.lexer, RecoveryPolicy.find_statement_border
                )
                error_node.info = error_tokens
                return error_node
        elif self.token.name in ["INT", "BOOLEAN"]:
            try:
                var = self.parse_var_decl()
                return var
            except SyntaxError as e:
                print(f"Error parsing variable declaration: {e}")
                error_node = VarDecl(0, PrimitiveType("int"), None)
                error_node.is_normal_node = False

                error_tokens = recovery(
                    self.lexer, RecoveryPolicy.find_statement_border
                )
                error_node.info = error_tokens
                return error_node
        else:
            try:
                exp = self.parse_expression()
            except Exception as e:
                print(f"Error parsing expression: {e}")
                error_node = Expression()
                error_node.is_normal_node = False

                error_tokens = recovery(
                    self.lexer, RecoveryPolicy.find_statement_border
                )
                error_node.info = error_tokens
                return error_node
            semi = self.accept("SEMI")
            if not semi:
                raise SyntaxError(
                    "Expected ';' at the end of statement", shared_str_to_terminal[";"]
                )
            return exp

    def parse_if_statement(self):
        """
        IfStatement: if ( Expression ) Statement [else Statement]
        """
        ifs = self.accept("IF")
        if not ifs:
            raise SyntaxError("Expected 'if' keyword", shared_str_to_terminal["if"])
        lparen = self.accept("LPAREN")
        if not lparen:
            raise SyntaxError("Expected '(' after 'if'", shared_str_to_terminal["("])
        cond = condition = self.parse_expression()
        if not condition:
            raise SyntaxError(
                "Expected condition expression", test_terminal_bool_literal
            )
        rparen = self.accept("RPAREN")
        if not rparen:
            raise SyntaxError(
                "Expected ')' after condition", shared_str_to_terminal[")"]
            )

        try:
            then_part = self.parse_statement()
        except SyntaxError as e:
            print(f"Error parsing then part of if statement: {e}")
            error_node = Statement()
            error_node.is_normal_node = False

            error_tokens = recovery(self.lexer, RecoveryPolicy.find_statement_border)
            error_node.info = error_tokens
            then_part = error_node

        else_part = None
        if self.token.name == "ELSE":
            self.next_token()
            try:
                else_part = self.parse_statement()
            except SyntaxError as e:
                print(f"Error parsing else part of if statement: {e}")
                error_node = Statement()
                error_node.is_normal_node = False

                error_tokens = recovery(
                    self.lexer, RecoveryPolicy.find_statement_border
                )
                error_node.info = error_tokens
                else_part = error_node

        return IfStatement(condition, then_part, else_part)

    def parse_ident(self):
        if self.token.name == "ID":
            ident = Ident(self.token.content)
            self.next_token()
            return ident
        else:
            return None

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
                raise SyntaxError(
                    "Expected variable type", shared_str_to_terminal["int"]
                )

            var_name = self.parse_ident()
            if not var_name:
                raise SyntaxError("Expected variable name", test_terminal_id)

            initialization = None
            if self.token.name == "EQ":
                eq = self.accept("EQ")
                if not eq:
                    raise SyntaxError("Expected '=' in variable declaration", eq)

                initialization = self.parse_expression()
                if not initialization:
                    raise SyntaxError(
                        "Expected initialization expression", test_terminal_int_literal
                    )

            semi = self.accept("SEMI")
            if not semi:
                raise SyntaxError(
                    "Expected ';' at the end of variable declaration",
                    shared_str_to_terminal[";"],
                )
            return VarDecl(access, var_type, initialization)

        except Exception as e:
            print(f"Error in variable declaration: {str(e)}")

    def parse_param_list(self):
        """
        ParamList: (Type ID (COMMA Type ID)*)
        """
        params = []
        lparen = self.accept("LPAREN")
        if not lparen:
            raise SyntaxError(
                "Expected '(' in parameter list", shared_str_to_terminal["("]
            )

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
            comma = self.accept("COMMA")
            if not comma:
                raise SyntaxError(
                    "Expected ',' in parameter list", shared_str_to_terminal[","]
                )

        rparen = self.accept("RPAREN")
        if not rparen:
            raise SyntaxError(
                "Expected ')' in parameter list", shared_str_to_terminal[")"]
            )
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
            raise SyntaxError("Expected return type", shared_str_to_terminal["int"])

        if self.token.name != "ID":
            raise SyntaxError("Expected method name", test_terminal_id)
        method_name = self.token.content
        self.next_token()

        try:
            params = self.parse_param_list()
        except SyntaxError as e:
            print(f"Error parsing parameter list: {e}")
            params = []

        body = None
        if self.token.name == "LBRACE":
            try:
                body = self.parse_block()
            except SyntaxError as e:
                print(f"Error parsing method body: {e}")
                error_node = Block([])
                error_node.is_normal_node = False

                error_tokens = recovery(
                    self.lexer, RecoveryPolicy.find_statement_border
                )
                error_node.info = error_tokens
                body = error_node
        else:
            semi = self.accept("SEMI")
            if not semi:
                raise SyntaxError(
                    "Expected ';' at the end of method declaration",
                    shared_str_to_terminal[";"],
                )
            body = Block([])

        return MethodDecl(access, return_type, method_name, params, body)

    def parse_block(self):
        """
        Block: { Statement* }
        """
        statements = []

        lbrace = self.accept("LBRACE")
        if not lbrace:
            raise SyntaxError(
                "Expected '{' at the beginning of block", shared_str_to_terminal["{"]
            )

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
        pack = self.accept("PACKAGE")
        if not pack:
            raise SyntaxError(
                "Expected 'package' keyword", shared_str_to_terminal["package"]
            )

        package_name = self.accept("ID")
        if not package_name:
            raise SyntaxError("Expected package name", test_terminal_id)

        semi = self.accept("SEMI")
        if not semi:
            raise SyntaxError(
                "Expected ';' after package declaration", shared_str_to_terminal[";"]
            )
        return PackageDecl(package_name.content)


if __name__ == "__main__":
    stream = """
    package pk;
    public class test{
        void func(int type) {
            int a = 1;
            if (true) {
                a = 2;
            } else {
                a = 3;
            }
        }
    }
    """
    p = Parser(stream)
    p.parse_compilation_unit()
