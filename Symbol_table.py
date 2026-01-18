from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


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
        #print("Looking up", name, "in scope", self.name)
        if name in self.symbols:
            return self.symbols[name]
        elif self.parent:
            return self.parent.lookup(name)
        else:
            return None

    def __repr__(self):
        return f"SymbolTable(symbols={self.symbols}, parent={self.parent})"

    def length(self):
        return len(self.symbols)


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
        print("No scope found for", name)
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

    def count_vars(self, name):
        count = 0
        for tabel in self.table.children:
            if tabel.name == name:
                for symbol in tabel.symbols.values():
                    #print(symbol)
                    if symbol.type == SymbolType.VARIABLE:
                        count += 1
        return count

    def dump(self, root: Optional[SymbolTable] = None, show_node: bool = False) -> str:

        # pretty-print the whole symbol table tree (scopes + symbols).
        # returns a string (so you can print() it or write to file).
        if root is None:
            root = self._get_root()

        lines = []
        self._dump_table(root, lines, indent=0, show_node=show_node)
        return "\n".join(lines)

    def _get_root(self) -> SymbolTable:
        t = self.table
        while t.parent is not None:
            t = t.parent
        return t

    def _dump_table(self, table: SymbolTable, out: list[str], indent: int, show_node: bool):
        pad = "  " * indent
        out.append(f"{pad}Scope: {table.name}")

        if not table.symbols:
            out.append(f"{pad}  (no symbols)")
        else:
            out.append(f"{pad}  Symbols:")
            for sym in sorted(table.symbols.values(),
                              key=lambda s: (s.type.name, s.slot if s.slot is not None else 10 ** 9, s.name)):
                slot_str = "-" if sym.slot is None else str(sym.slot)
                node_str = ""
                if show_node:
                    node_str = f"  node={type(sym.node).__name__}"
                out.append(f"{pad}    {sym.name:<12} {sym.type.name:<8} {sym.data_type:<10} slot={slot_str}{node_str}")

        if table.children:
            out.append(f"{pad}  Children:")
            for child in table.children:
                self._dump_table(child, out, indent + 1, show_node=show_node)

