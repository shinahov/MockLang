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
        "class": "CLASS",
        "end": "END",
        "to": "TO",
        "void": "TYPE_VOID",
    }
    TWO = {"->": "ARROW",
           "=?": "EQUALSQ",
           }

    ONE = {
        "=": "EQ", "+": "PLUS", "-": "MINUS", "*": "STAR", "/": "SLASH",
        "<": "LT", ">": "GT",
        "(": "LP", ")": "RP", ",": "COMMA", ";": "SEMI",
        ":": "COLON", ".": "DOT", "[": "LBRK", "]": "RBRK",
    }


