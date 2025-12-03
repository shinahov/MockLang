import os, sys, re
import Tokenizer
import Parser
import SymbolAnalyzer as SA
import Symbol_table as ST

class VMGenerator:
    def __init__(self, symbol_table_manager, program):
        self.symbol_table_manager = symbol_table_manager
        self.program = program
        self.instructions = []
        self.class_name = ""

    def generate(self):
        self.generate_class()

        return self.instructions

    def generate_class(self):
        assert self.program[0].type == "CLASS_DEF"
        self.class_name = self.program[0].value
        assert self.program[1].type == "FIELDS"
        assert self.program[2].type == "BODY"
        body = self.program[2]
        result = self.generate_class_body(body)

    def generate_class_body(self, body):
        for statement in body.value:
            if statement.type == "METHOD_DEF":
                methode = statement.value
                assert methode[0].type == "NAME"
                assert methode[1].type == "ARGS"
                assert methode[2].type == "RETURN_TYPE"
                assert methode[3].type == "BODY"
                self.generate_method(methode)
            elif statement.type == "FN_DEF":
                FN_body = statement.value
                body = FN_body.value
                assert body[0].type == "NAME"
                assert body[1].type == "ARGS"
                assert body[2].type == "RETURN_TYPE"
                assert body[3].type == "BODY"
                self.generate_function(body)
            elif statement.type == "CREATE_STMT":
                crate_stmt = statement.value
                assert crate_stmt[0].type == "TYPE"
                assert crate_stmt[1].type == "IDENT"
                self.generate_create_statement(crate_stmt)
            return None

    def generate_method(self, methode):
        pass

    def generate_function(self, body):
        pass

    def generate_create_statement(self, crate_stmt):
        if len(crate_stmt) == 4:
            var_type = crate_stmt[0].value
            var_name = crate_stmt[1].value
            symbol = self.parse_symbol(var_name)
            print(symbol)
            return
            assert crate_stmt[2].type == "EQ"
            expr = crate_stmt[3]
            self.generate_expression(expr)
            self.pop()

    def parse_symbol(self, var_name):
        symbol = self.symbol_table_manager.table.lookup(var_name)
        if symbol is None:
            raise Exception(f"Undefined variable '{var_name}'")
        segment = None
        if symbol.type == ST.SymbolType.VARIABLE:  # lokale Variable
            segment = "local"
        elif symbol.type == ST.SymbolType.FIELD:
            segment = "this"
        elif symbol.type == ST.SymbolType.PARAM:
            segment = "argument"
        else:
            raise Exception(f"Unsupported symbol type for '{var_name}'")
        return (f"{segment} {symbol.slot}")



