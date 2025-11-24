from dataclasses import dataclass
from enum import Enum, auto

class SymbolType(Enum):
    VARIABLE = auto()
    PARAM = auto()
    FUNCTION = auto()
    FIELD = auto()
    CLASS = auto()
    TYPE = auto()

@dataclass
class Symbol:
    name: str
    type: SymbolType
    data_type: str
    node: object  # Reference to the AST node

class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def define(self, name, symbol_type, data_type, node):
        if name in self.symbols:
            raise Exception(f"Symbol '{name}' already defined in current scope")
        symbol = Symbol(name, symbol_type, data_type, node)
        self.symbols[name] = symbol
        return symbol

    def lookup(self, name):
        if name in self.symbols:
            return self.symbols[name]
        elif self.parent:
            return self.parent.lookup(name)
        else:
            return None

    def __repr__(self):
        return f"SymbolTable(symbols={self.symbols}, parent={self.parent})"