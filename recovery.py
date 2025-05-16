from lexer import Lexer
from tokens import Token
from enum import Enum, unique

"""
在parse的不同阶段应使用不同的错误恢复策略，以寻找各种不同的恐慌恢复停止位置。
现在大致分为这四类阶段，比如说在顶层我们遇到package, public, protected, 
private, class这些可能为一个类的开头的元素才停止。而在表达式层我们可能遇到
+, -等等运算符号就要停止，因为遇到它时一个表达式一定已经结束了。
"""
@unique
class RecoveryPolicy(Enum):
    find_toplevel_border = 0
    find_class_member_border = 1
    find_statement_border = 2
    find_expression_border = 3

"""
对lexer应用recovery，使其解析位置直接跳转到右界，并返回所有被跳过的token。
lexer: 要执行恢复的词法分析器
policy: 要选择的恢复策略
还没写好
"""
def recovery(lexer: Lexer, policy: RecoveryPolicy) -> list[Token]:
    return []
