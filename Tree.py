from tokens import Token

"""
====================
       树结点
====================
is_normal_node: bool, 该结点是一个正常结点，还是一个包含错误子串的未解析成功的结点。
info: list[Token], 打包起来的错误子串，最后我们要根据这个错误子串来将这个结点修复为正确结点。
"""
class Tree:
    def __init__(self):
        self.is_normal_node = True
        self.info: list[Token] = []
        return

"""
====================
       类定义
====================
access: int, 访问权限，0表示未设定，1表示private，2表示protected，3表示public
class_name: str, 类名
defs: list[Tree], 类体，类体中只能有
"""
class ClassDecl(Tree):
    def __init__(self, access: int, class_name: str, defs: list[Tree]):
        super().__init__()
        self.name = class_name
        self.defs = defs
        self.access = access
        return

"""
====================
        文件
====================
package_decl: str, 包名
defs: list[ClassDecl], 该文件下的所有类定义
"""
class CompilationUnit(Tree):
    def __init__(self, pack_name: str, defs: list[ClassDecl]):
        super().__init__()
        self.package_decl = pack_name
        self.defs = defs

    def add_def(self, class_decl):
        self.defs.append(class_decl)

    def set_pack(self, pack):
        self.package_decl = pack

"""
====================
        语句
====================
抽象地表示一个语句
"""
class Statement(Tree):
    def __init__(self):
        super().__init__()
        return

"""
====================
       表达式
====================
抽象地表示一个表达式
"""
class Expression(Tree):
    def __init__(self):
        super().__init__()
        return

"""
====================
         块
====================
defs: list[Statement], 块中所有语句
"""
class Block(Tree):
    def __init__(self, defs: list[Statement]):
        super().__init__()
        self.defs = defs
        return

"""
====================
      变量定义
====================
access: int, 访问权限。如果在块中作为局部变量定义的话，access只能为0。
var_type: Expression, 变量的类型
initialization: Expression, 变量的初始化表达式
"""
class VarDecl(Statement):
    def __init__(self, access: int, var_type: Expression, initialization: Expression):
        super().__init__()
        self.access = access
        self.var_type = var_type
        self.initialization = initialization
        return

"""
====================
       if语句
====================
cond: Expression, 条件表达式
then_part: Statement, if(...) {then_part} else {else_part}
else_part: Statement, if(...) {then_part} else {else_part}
"""
class IfStatement(Statement):
    def __init__(self, cond: Expression, then_part: Statement, else_part: Statement):
        super().__init__()
        self.cond = cond
        self.then_part = then_part
        self.else_part = else_part

"""
====================
     基本类型结点
====================
tag: str，表示何种基本类型，比如int基本类型就是"int"
"""
class PrimitiveType(Expression):
    def __init__(self, type_tag: str):
        super().__init__()
        self.tag = type_tag

'''
====================
       标识符
====================
name: str, 标识符的名称
'''
class Ident(Expression):
    def __init__(self, name):
        super().__init__()
        self.name = name

"""
====================
      方法定义
====================
access: int, 访问权限
restype: Expression, 方法的返回类型
name: str, 方法的名称
params: list[VarDecl], 方法的参数列表
body: Block, 方法体
"""
class MethodDecl(Tree):
    def __init__(self, access: int, restype: Expression, name: str, params: list[VarDecl], body: Block):
        super().__init__()
        self.restype = restype
        self.name = name
        self.params = params
        self.body = body
        self.access = access

"""
====================
       字面量
====================
type_tag: str, 表示何种基本类型，比如int基本类型就是"int"
value: 具体值
"""
class Literal(Expression):
    def __init__(self, type_tag: str, value):
        super().__init__()
        self.type_tag = type_tag
        self.value = value
