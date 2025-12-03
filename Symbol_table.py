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
    slot: int


class SymbolTable:
    def __init__(self, parent=None, name="class_scope"):
        self.symbols = {}
        self.parent = parent
        self.children = []
        self.name = name

    def define(self, name, symbol_type, data_type, node, slot=None):
        if name in self.symbols:
            raise Exception(f"Symbol '{name}' already defined in current scope")
        symbol = Symbol(name, symbol_type, data_type, node, slot)
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


class SymbolTableManager:
    def __init__(self):
        self.table: SymbolTable = SymbolTable(parent=None)

    def enter_scope(self, name):
        self.table = SymbolTable(parent=self.table, name=name)
        self.table.parent.children.append(self.table)

    def enter_scope_for_lookup(self, name):
        for tabel in self.table.children:
            if tabel.name == name:
                self.table = tabel
                return

    def exit_scope(self):
        if self.table.parent is not None:
            self.table = self.table.parent
        else:
            raise Exception("Cannot exit global scope")

    def define(self, name, symbol_type, data_type, node, slot=None):
        return self.table.define(name, symbol_type, data_type, node, slot)

    def lookup(self, name):
        if self.table is None:
            raise Exception("No symbol table available")
        if self.table.lookup(name) is None:
            raise Exception(f"Symbol '{name}' not found")
        return self.table.lookup(name)
