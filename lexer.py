from tokens import *

"""
简单词法分析器，直接用就行
"""
class Lexer:
    def __init__(self, stream: str):
        self.stream = stream
        self.n = len(stream)
        self.ptr = 0
        self.buf = []
        self.current = self.stream[self.ptr]
        return

    def next_char(self):
        if self.current == "end_of_stream":
            return
        if self.ptr + 1 >= self.n:
            self.current = "end_of_stream"
            return
        else:
            self.ptr += 1
            self.current = self.stream[self.ptr]

    def next(self) -> Token:
        while self.current in [' ', '\n', '\t']:
            self.next_char()
        if self.ptr >= self.n or self.current == "end_of_stream":
            return eof
        if '0' <= self.current <= '9':
            return self.parse_int()
        elif self.current in [';', '{', '}', '=', '(', ')']:
            token = shared_str_to_terminal[self.current]
            self.next_char()
            return token
        else:
            return self.parse_word()

    def set_pos(self, pos: int):
        if pos < self.n:
            self.ptr = pos
            self.buf = []
            self.current = self.stream[self.ptr]

    def parse_int(self) -> Token:
        self.buf = []
        while '0' <= self.current <= '9':
            self.buf.append(self.current)
            self.next_char()
        if self.current in [' ', '\n', '\t', ';']:
            return Token("INT_LITERAL", int("".join(self.buf)))
        else:
            self.skip(["(", ")", "{", "}", "=", ";", " ", "\n", "\t"])
            return test_terminal_illegal_token

    def parse_word(self) -> Token:
        self.buf = []
        while self.current not in ["(", ")", "{", "}", "=", ";", " ", "\n", "\t", "end_of_stream"]:
            self.buf.append(self.current)
            self.next_char()
        word = "".join(self.buf)
        if word in shared_str_to_terminal.keys():
            return shared_str_to_terminal[word]
        else:
            return Token("ID", word)

    def skip(self, expect: list[str]):
        expect.append("end_of_stream")
        while self.current not in expect:
            self.next_char()
    
    def __len__(self):
        return self.n

if __name__ == '__main__':
    stream = '''
    package pk;
    public class test{
        void func(int type) {
            int a = 1;
            if (true) {
                
            } else {
            
            }
        }
    }
    '''
    l = Lexer(stream)
