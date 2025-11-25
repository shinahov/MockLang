from Symbol_table import SymbolType
import Tokenizer


class SymbolAnalyzer:
    def __init__(self, symbol_table_manager, program):
        self.symbol_table_manager = symbol_table_manager
        self.program = program

    def analyze(self):
        class_def = self.program[0]
        fields = self.program[1]
        body = self.program[2]
        for name, type in fields.value:
            self.symbol_table_manager.define(
                name,
                SymbolType.FIELD,
                type,
                Tokenizer.Token(type, name)
            )
        print("Symbol Table after analysis:")
        print(self.symbol_table_manager.table)
        


