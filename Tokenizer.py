import re

class Token:
    __SLOTS__ = ('type', 'value')
    def __init__(self, type_, value):
        self.type = type_
        self.value = value
    def __repr__(self):
        return f"Token({self.type}, {self.value})"


class Tokenizer:
    KEYWORDS = {
        "fn": "FN",
        "create": "CREATE",
        "set": "SET",
        "if": "IF",
        "else": "ELSE",
        "loop": "LOOP",
        "while": "WHILE",
        "return": "RETURN",
        "print": "PRINT",
        "int": "TYPE_INT",
        "float": "TYPE_FLOAT",
        "String": "TYPE_STRING",
        "class": "CLASS",
        "end": "END",
        "to": "TO",
        "void": "TYPE_VOID",
        "false": "FALSE",
        "true": "TRUE",
        "self": "SELF"
    }
    TWO = {"->": "ARROW",
           "=?": "EQUALSQ",
           "<=": "LE",
           ">=": "GE",
           "!=": "NE"
           }

    ONE = {
        "=": "EQ", "+": "PLUS", "-": "MINUS", "*": "STAR", "/": "SLASH",
        "<": "LT", ">": "GT",
        "(": "LP", ")": "RP", ",": "COMMA", ";": "SEMI",
        ":": "COLON", ".": "DOT", "[": "LBRK", "]": "RBRK", "{": "LBRACE", "}": "RBRACE",
    }

    comperators = {"EQ", "EQUALSQ", "LT", "GT", "LE", "GE", "NE"}
    operators = {"PLUS", "MINUS", "STAR", "SLASH"}
    def tokenize(self, code):
        tokens = []
        i = 0
        while i < len(code):
            #print(f"Processing character '{code[i]}' at position {i}")
            if code[i].isspace():
                i += 1
                continue
            if code[i:i+2] in self.TWO:
                tokens.append(Token(self.TWO[code[i:i+2]], code[i:i+2]))
                i += 2
                continue
            if code[i] in self.ONE:
                tokens.append(Token(self.ONE[code[i]], code[i]))
                i += 1
                continue
            if code[i].isalpha() or code[i] == '_':
                start = i
                while i < len(code) and (code[i].isalnum() or code[i] == '_'):
                    i += 1
                word = code[start:i]
                if word in self.KEYWORDS:
                    tokens.append(Token(self.KEYWORDS[word], word))
                elif re.match(r'^[A-Z][A-Za-z0-9_]*$', word):
                    #print(f"Identified class identifier: {word}")
                    if word == "END":
                        #print("Identified END keyword as class identifier")
                        tokens.append(Token("END", word))
                    else:
                        tokens.append(Token("CLASS_NAME", word))
                else:
                    tokens.append(Token("IDENT", word))
                continue
            if code[i].isdigit():
                start = i
                dot = False
                while i < len(code) and (code[i].isdigit() or code[i] == '.'):
                    if code[i] == '.':
                        if dot:
                            print(f"Error: invalid number format with multiple dots '{code[start:i+1]}' at position {i}")
                            break
                        dot = True
                    i += 1
                number = code[start:i]
                if dot:
                    tokens.append(Token("FLOAT", float(number)))
                else:
                    tokens.append(Token("INT", int(number)))
                continue
            if code[i] == '"':
                i += 1
                start = i
                while i < len(code) and code[i] != '"':
                    i += 1
                if i >= len(code):
                    print(f"Error: unterminated string starting at position {start-1}")
                    break
                string_value = code[start:i]
                tokens.append(Token("STRING", string_value))
                i += 1
                continue
            print(f"Error: unrecognized character '{code[i]}' at position {i}")


            i += 1
        tokens.append(Token("EOF", None))
        return tokens









