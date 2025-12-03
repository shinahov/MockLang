from Symbol_table import SymbolType
import Tokenizer





class SymbolAnalyzer:
    def __init__(self, symbol_table_manager, program):
        self.symbol_table_manager = symbol_table_manager
        self.program = program

    def analysed_body(self, body):
        var_slots = 0
        for statement in body.value:
            # print("type and value", statement.type, statement.value)
            if statement.type == "METHOD_DEF":
                methode = statement.value
                assert methode[0].type == "NAME"
                assert methode[1].type == "ARGS"
                assert methode[2].type == "RETURN_TYPE"
                assert methode[3].type == "BODY"
                #print(methode[1].value)
                self.analyze_method(methode)
            elif statement.type == "FN_DEF":
                FN_body = statement.value
                body = FN_body.value
                assert body[0].type == "NAME"
                assert body[1].type == "ARGS"
                assert body[2].type == "RETURN_TYPE"
                assert body[3].type == "BODY"
                self.analyze_function(body)

            elif statement.type == "CREATE_STMT":
                crate_stmt = statement.value
                assert crate_stmt[0].type == "TYPE"
                assert crate_stmt[1].type == "IDENT"
                var_type = crate_stmt[0].value
                var_name = crate_stmt[1].value
                self.symbol_table_manager.define(
                    var_name,
                    SymbolType.VARIABLE,
                    var_type,
                    crate_stmt[1],
                    slot=var_slots
                )
                var_slots += 1
            #print("Symbol Table after analysing statement:")
            #print(self.symbol_table_manager.table)





    def analyze(self):
        field_slot = 0
        class_def = self.program[0]
        fields = self.program[1]
        body = self.program[2]
        for name, type in fields.value:
            self.symbol_table_manager.define(
                name,
                SymbolType.FIELD,
                type,
                Tokenizer.Token(type, name),
                slot=field_slot
            )
            field_slot += 1
        self.analysed_body(body)
        return self.symbol_table_manager

    def analyze_method(self, methode):
        name = methode[0].value
        args = methode[1].value
        return_type = methode[2].value
        body = methode[3].value

        self.symbol_table_manager.enter_scope(name)
        self.symbol_table_manager.define(
            "self",
            SymbolType.PARAM,
            "SELF",
            Tokenizer.Token("SELF", "self"),
            slot=0
        )

        if len(args) % 3 != 0:
            raise Exception(f"Method '{name}' has mismatched argument names and types")
        self.analysed_args(args, slots=1)  # Start slots from 1 to reserve 0 for 'self'
        self.analysed_method_body(body)
        self.symbol_table_manager.exit_scope()

    def analysed_args(self, args, slots=0):
        args_slot = slots
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
                ident_tok,
                slot=args_slot
            )
            args_slot += 1

        #print("Symbol Table after analysing args:")
        #print(self.symbol_table_manager.table)

    def analysed_method_body(self, body):
        var_slots = 0
        for statement in body:
            if statement.type == "CREATE_STMT":
                crate_stmt = statement.value
                assert crate_stmt[0].type == "TYPE"
                assert crate_stmt[1].type == "IDENT"
                var_type = crate_stmt[0].value
                var_name = crate_stmt[1].value
                self.symbol_table_manager.define(
                    var_name,
                    SymbolType.VARIABLE,
                    var_type,
                    crate_stmt[1],
                    slot=var_slots
                )
                var_slots += 1

    def analyze_function(self, FN_body):
        name = FN_body[0].value
        args = FN_body[1].value
        return_type = FN_body[2].value
        body = FN_body[3].value

        self.symbol_table_manager.enter_scope(name)


        if len(args) % 3 != 0:
            raise Exception(f"Method '{name}' has mismatched argument names and types")
        self.analysed_args(args, slots=0)  # Start slots from 1 to reserve 0 for 'self'
        self.analysed_method_body(body)
        self.symbol_table_manager.exit_scope()




