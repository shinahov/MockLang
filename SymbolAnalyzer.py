from Symbol_table import SymbolType
import Tokenizer





class SymbolAnalyzer:
    def __init__(self, symbol_table_manager, program):
        self.symbol_table_manager = symbol_table_manager
        self.program = program

    def analysed_body(self, body, field_slot):
        var_slots = field_slot
        for statement in body.value:
            # print("type and value", statement.type, statement.value)
            if statement.type == "METHOD_DEF":
                methode = statement.value
                assert methode[0].type == "NAME"
                assert methode[1].type == "ARGS"
                assert methode[2].type == "RETURN_TYPE"
                assert methode[3].type == "BODY"
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
                    SymbolType.FIELD,
                    var_type,
                    crate_stmt[1],
                    slot=var_slots
                )
                var_slots += 1
            elif statement.type == "LOOP_STMT":
                loop_body = statement.value
                assert loop_body.type == "LOOP_BODY"
                assert loop_body.value[0].type == "IDENT"
                loop_var_tok = loop_body.value[0]
                loop_var = loop_var_tok.value
                if self.symbol_table_manager.table.lookup(loop_var) is None:
                    self.symbol_table_manager.define(
                        loop_var,
                        SymbolType.VARIABLE,
                        "int",
                        loop_var_tok,
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
        self.analysed_body(body, field_slot)
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

            assert ident_tok.type == "IDENT", (f"Arg #{i // 3}: "
                                               f"expected IDENT, got {ident_tok.type} "
                                               f"({ident_tok.value!r})")
            assert colon_tok.type == "COLON", (f"Arg #{i // 3}: "
                                               f"expected COLON, got {colon_tok.type} "
                                               f"({colon_tok.value!r})")
            assert type_tok.type.startswith(
                "TYPE_"), (f"Arg #{i // 3}: expected TYPE_*, got "
                           f"{type_tok.type} ({type_tok.value!r})")

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

    def analysed_method_body(self, body):
        print("Analysing method body...")
        print(body)
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
            elif statement.type == "LOOP_STMT":
                loop_body = statement.value
                assert loop_body.type == "LOOP_BODY"
                assert loop_body.value[0].type == "IDENT"
                loop_var_tok = loop_body.value[0]
                loop_var = loop_var_tok.value
                if self.symbol_table_manager.table.lookup(loop_var) is None:
                    self.symbol_table_manager.define(
                        loop_var,
                        SymbolType.VARIABLE,
                        "int",
                        loop_var_tok,
                        slot=var_slots
                    )
                    var_slots += 1
            elif statement.type == "IF_STMT":
                body = statement.value
                #print("IF_ELSE_BODY with length:", len(body.value))
                if body.type == "IF_ELSE_STMT":
                    assert len(body.value) == 3
                    if_body = body.value[1]
                    else_body = body.value[2]
                    #print("if  body   ", if_body)
                    #print("else body   ", else_body)
                    self.analysed_method_body(if_body)
                    self.analysed_method_body(else_body)
                elif body.type == "IF_STMT":
                    assert len(body.value) == 2
                    if_body = body.value[1]
                    #print(if_body)
                    self.analysed_method_body(if_body)




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




