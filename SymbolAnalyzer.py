from Symbol_table import SymbolType
import Tokenizer





class SymbolAnalyzer:
    def __init__(self, symbol_table_manager, program):
        self.symbol_table_manager = symbol_table_manager
        self.program = program

    def analysed_body(self, body):
        for statement in body.value:
            # print("type and value", statement.type, statement.value)
            if statement.type == "METHOD_DEF":
                methode = statement.value
                assert methode[0].type == "NAME"
                assert methode[1].type == "ARGS"
                assert methode[2].type == "RETURN_TYPE"
                assert methode[3].type == "BODY"
                print(methode[1].value)
                self.analyze_method(methode)



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

        self.analysed_body(body)

    def analyze_method(self, methode):
        name = methode[0].value
        args = methode[1].value
        return_type = methode[2].value
        body = methode[3].value

        self.symbol_table_manager.enter_scope()

        if len(args) % 3 != 0:
            raise Exception(f"Method '{name}' has mismatched argument names and types")
        self.analysed_args(args)

    def analysed_args(self, args):
        for i in range(0, len(args), 3):
            ident_tok = args[i]
            colon_tok = args[i + 1]
            type_tok = args[i + 2]

            assert ident_tok.type == "IDENT"
            assert colon_tok.type == "COLON"
            assert type_tok.type.startswith("TYPE_")

            arg_name = ident_tok.value
            arg_type = type_tok.value

            self.symbol_table_manager.define(
                arg_name,
                SymbolType.PARAM,
                arg_type,
                ident_tok
            )

        print("Symbol Table after analysing args:")
        print(self.symbol_table_manager.table)



