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
        self.goto_count = 0

    def generate(self):
        self.generate_class()

        return self.instructions

    def generate_class(self):
        assert self.program[0].type == "CLASS_DEF"
        self.class_name = self.program[0].value
        assert self.program[1].type == "FIELDS"
        assert self.program[2].type == "BODY"
        body = self.program[2]
        self.constructor_generator(self.program[1].value, body)
        self.generate_class_body(body)

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
                pass
            else:
                raise Exception(f"Unsupported statement type '{statement.type}' in class body")
            #return None

    def generate_method(self, methode):
        name = methode[0].value
        local_count = self.symbol_table_manager.count_vars(name)
        self.instructions.append(f"function {self.class_name}.{name} {local_count}")
        #push self pointer
        self.push_symbol("argument 0")
        self.pop_symbol("pointer 0")
        #print(self.instructions)
        assert methode[3].type == "BODY"
        body = methode[3]
        assert methode[1].type == "ARGS"
        assert methode[2].type == "RETURN_TYPE"
        return_types = methode[2].value
        self.generate_method_body(body, name)
        #print("return types", return_types)
        if len(return_types) == 1 and return_types[0].type == "TYPE_VOID":
            self.instructions.append("push constant 0")
            self.instructions.append("return")




    def generate_function(self, body):
        name = body[0].value
        local_count = self.symbol_table_manager.count_vars(name)
        self.instructions.append(f"function {self.class_name}.{name} {local_count}")
        assert body[3].type == "BODY"
        fn_body = body[3]
        assert body[1].type == "ARGS"
        assert body[2].type == "RETURN_TYPE"
        return_types = body[2].value
        self.generate_method_body(fn_body, name)
        #print("return types", return_types)
        if len(return_types) == 1 and return_types[0].type == "TYPE_VOID":
            self.instructions.append("push constant 0")
            self.instructions.append("return")


    def generate_create_statement(self, crate_stmt):
        if len(crate_stmt) == 4:
            var_type = crate_stmt[0].value
            var_name = crate_stmt[1].value
            symbol = self.parse_symbol(var_name)
            assert crate_stmt[2].type == "EQ"
            expr = crate_stmt[3]
            self.generate_expression(expr)
            self.pop_symbol(symbol)


    def parse_symbol(self, var_name):
        symbol = self.symbol_table_manager.table.lookup(var_name)
        #print(self.symbol_table_manager.table)
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

    def generate_expression(self, expr):
        print("generating expression", expr)

        if isinstance(expr, Tokenizer.Token) and expr.type == "TERM":
            return self.generate_expression(expr.value)
        if not (isinstance(expr, Tokenizer.Token) and expr.type == "EXPR"):
            return self.write_value(expr)


        parts = expr.value
        if len(parts) == 1:
            single = parts[0]
            if isinstance(single, Tokenizer.Token) and single.type in ("EXPR", "TERM"):
                return self.generate_expression(single)
            else:
                return self.write_value(single)

        if len(parts) == 3:
            left, middle, right = parts

            if middle.type == "OPERATOR":
                operator = middle.value
                self.generate_expression(left)
                self.generate_expression(right)
                if operator == "+":
                    self.instructions.append("add")
                elif operator == "-":
                    self.instructions.append("sub")
                elif operator == "*":
                    self.instructions.append("call Math.multiply 2")
                elif operator == "/":
                    self.instructions.append("call Math.divide 2")
                else:
                    raise Exception(f"Unsupported operator '{operator}' in expression")

            # COMPARATOR: =? < > ...
            elif middle.type == "COMPERATOR":
                comparator = middle.value
                self.generate_expression(left)
                self.generate_expression(right)
                if comparator == "=?":
                    self.instructions.append("eq")
                elif comparator == "<":
                    self.instructions.append("lt")
                elif comparator == ">":
                    self.instructions.append("gt")
                else:
                    raise Exception(f"Unsupported comparator '{comparator}' in expression")

            elif middle.type == "DOT":
                if right.type == "FN_CALL":
                    fn_call = right.value
                    fn_name = fn_call[0].value
                    args = fn_call[1].value
                    self.generate_expression(left)
                    for arg in args:
                        self.generate_expression(arg)
                    self.instructions.append(f"call {self.class_name}.{fn_name} {len(args) + 1}")

                elif right.type == "IDENT":
                    var_name = right.value
                    self.generate_expression(left)
                    slot = self.symbol_table_manager.lookup(var_name)
                    if slot is None:
                        raise Exception(f"Undefined variable '{var_name}'")
                    if slot.type != ST.SymbolType.FIELD:
                        raise Exception(f"Variable '{var_name}' is not a field")
                    self.instructions.append(f"push this {slot.slot}")
                else:
                    raise Exception(f"Unsupported right side of DOT: {right}")

            else:
                raise Exception(f"Unsupported middle token in expression: {middle}")

            return

        print("complex expression", expr)
        raise Exception("Complex expressions are not supported yet expr: " + repr(expr))

    def write_value(self, param):
        if param.type == "INT":
            self.instructions.append(f"push constant {param.value}")
        elif param.type == "FLOAT":
            self.instructions.append(f"push constant {param.value}")
        elif param.type == "STRING":
            self.instructions.append(f'push string "{param.value}"')
        elif param.type == "IDENT":
            symbol = self.parse_symbol(param.value)
            self.instructions.append(f"push {symbol}")
        else:
            raise Exception(f"Unsupported parameter type '{param.type}'")

    def pop_symbol(self, symbol):
        self.instructions.append(f"pop {symbol}")
        
    def push_symbol(self, symbol):
        self.instructions.append(f"push {symbol}")

    def generate_method_body(self, body, method_name):
        self.symbol_table_manager.enter_scope_for_lookup(method_name)
        for statement in body.value:
            #print(statement)
            if statement.type == "SET_STMT":
                set_stmt = statement.value
                self.generate_set_statement(set_stmt, method_name)
            elif statement.type == "PRINT_STMT":
                print_stmt = statement.value
                self.generate_print_statement(print_stmt)
            elif statement.type == "RETURN_STMT":
                return_stmt = statement.value
                self.generate_return_statement(return_stmt)
            elif statement.type == "CREATE_STMT":
                crate_stmt = statement.value
                self.generate_create_statement(crate_stmt)
            elif statement.type == "IF_STMT":
                #print(statement)
                if_stmt = statement.value
                self.generate_if_statement(if_stmt)
            elif statement.type == "FN_CALL":
                fn_call = statement.value
                self.generate_function_call(fn_call)
                self.pop_symbol("temp 0")
            elif statement.type == "LOOP_STMT":
                assert statement.value.type == "LOOP_BODY"
                loop_body = statement.value
                assert len(loop_body.value) == 4
                assert loop_body.value[0].type == "IDENT"
                loop_var = loop_body.value[0].value
                assert loop_body.value[1].type == "START_EXPR"
                start_expr = loop_body.value[1].value
                assert loop_body.value[2].type == "END_EXPR"
                end_expr = loop_body.value[2].value
                body_stmt = loop_body.value[3]
                self.generate_loop_statement(loop_var, start_expr, end_expr, body_stmt, method_name)
        self.symbol_table_manager.exit_scope()



    def generate_set_statement(self, set_stmt, method_name):
        if len(set_stmt) == 3:
            calss_var = set_stmt[0]
            var = set_stmt[1]
            assert set_stmt[2].type == "TO"
            expr = set_stmt[2].value
            self.generate_expression(expr)
            if calss_var.type == "IDENT":
                pass # TODO for other cases

            elif calss_var.type == "SELF":
                slot = self.symbol_table_manager.lookup(var.value)
                while slot.type != ST.SymbolType.FIELD:
                    self.symbol_table_manager.exit_scope()
                    slot = self.symbol_table_manager.lookup(var.value)
                self.symbol_table_manager.enter_scope_for_lookup(method_name)
                #print(self.symbol_table_manager.table.symbols)
                self.pop_symbol(f"this {slot.slot}")



    def generate_print_statement(self, print_stmt):
        expr = print_stmt
        self.generate_expression(expr)
        type = self.infer_type(expr)
        self.instructions.append(f"call print.{type} 1")

    def generate_return_statement(self, return_stmt):
        for expr in return_stmt:
            #print("expressions in return", expr)
            if len(expr) == 1:
                self.write_value(expr[0])
            elif len(expr) == 2:
                if expr[0].value == "self":
                    slot = self.symbol_table_manager.lookup(expr[1].value)
                    self.push_symbol(f"this {slot.slot}")
                #todo for other cases
        self.instructions.append("return")




    def generate_if_statement(self, if_stmt):
        label_id = self.get_new_label_id()
        Parser.pretty_print(if_stmt)
        if_token = if_stmt.value[1]
        print("if token", if_token)
        else_token = None
        if if_stmt.type == "IF_ELSE_STMT":
            else_token = if_stmt.value[2]
            print("else token", else_token)
        assert if_stmt.value[0].type == "EXPR"
        condition = if_stmt.value[0]
        tokens = condition.value
        for i, token in enumerate(tokens):
            if token.type == "COMPERATOR":
                left = tokens[:i]
                right = tokens[i+1:]
                comp = token.value
        self.generate_expression(Tokenizer.Token("EXPR", left))
        self.generate_expression(Tokenizer.Token("EXPR", right))
        if comp == "=?":
            self.instructions.append("eq")
        elif comp == "<":
            self.instructions.append("lt")
        elif comp == ">":
            self.instructions.append("gt")
        else:
            raise Exception(f"Unsupported comparator '{comp}' in if statement")
        self.instructions.append("if-goto IF_TRUE" + str(label_id))
        self.instructions.append("goto IF_FALSE" + str(label_id))
        self.instructions.append("label IF_TRUE" + str(label_id))
        self.generate_statmen(if_token)
        if else_token is not None:
            self.instructions.append("goto IF_END" + str(label_id))
            self.instructions.append("label IF_FALSE" + str(label_id))
            self.generate_statmen(else_token)
            self.instructions.append("label IF_END" + str(label_id))
        #label_id = self.get_new_label_id()

    def generate_function_call(self, fn_call):
        name = fn_call[0].value
        args = fn_call[1].value
        for arg in args:
            if arg.type == "INT" or arg.type == "FLOAT":
                self.instructions.append(f"push constant {arg.value}")
            elif arg.type == "IDENT":
                symbol = self.parse_symbol(arg.value)
                self.instructions.append(f"push {symbol}")
        self.instructions.append(f"call {name} {len(args)}")

    def constructor_generator(self, value, body):
        field_count = self.symbol_table_manager.table.length()
        self.instructions.append(f"function {self.class_name}.new 0")
        self.instructions.append(f"push constant {field_count}")
        self.instructions.append("call Memory.alloc 1")
        self.instructions.append("pop pointer 0")
        args = len(value)
        self.push_args(args)
        for token in body.value:
            if token.type == "CREATE_STMT":
                crate_stmt = token.value
                if len(crate_stmt) == 4:
                    expr = crate_stmt[3]
                    self.generate_expression(expr)
                self.pop_symbol("this " + str(args))
                args += 1
        self.push_symbol("pointer 0")
        self.instructions.append("return")






    def push_args(self, args):
        for i in range(args):
            self.push_symbol(f"argument {i}")
            self.pop_symbol(f"this {i}")

    def return_statment(self, expr):
        pass
        #print(expr)

    def generate_statmen(self, if_token):
        for statement in if_token:
            print("statment ", statement)
            if statement.type == "SET_STMT":
                set_stmt = statement.value
                self.generate_set_statement(set_stmt, "")
            elif statement.type == "PRINT_STMT":
                print_stmt = statement.value
                self.generate_print_statement(print_stmt)
            elif statement.type == "RETURN_STMT":
                return_stmt = statement.value
                self.generate_return_statement(return_stmt)
            elif statement.type == "CREATE_STMT":
                crate_stmt = statement.value
                self.generate_create_statement(crate_stmt)
            elif statement.type == "FN_CALL":
                fn_call = statement.value
                self.generate_function_call(fn_call)
                self.pop_symbol("temp 0")
        #self.instructions.append("label IF_FALSE" + str(self.goto_count))


    def infer_type(self, expr):
        if expr.type == "TERM":
            return self.infer_type(expr.value)

        if expr.type == "EXPR":
            parts = expr.value
            if len(parts) == 1:
                return self.infer_type(parts[0])
            elif len(parts) == 3:
                left, middle, right = parts
                if middle.type == "OPERATOR":
                    left_type = self.infer_type(left)
                    right_type = self.infer_type(right)
                    if left_type == "float" or right_type == "float":
                        return "float"
                    else:
                        return "int"
                elif middle.type == "COMPERATOR":
                    return "int"
                elif middle.type == "DOT":
                    return self.infer_type(right)
            raise Exception(f"Cannot infer type for complex expression: {expr}")
        return self.get_instance_type(expr)

    def get_instance_type(self, expr):
        if expr.type == "INT":
            return "int"
        elif expr.type == "FLOAT":
            return "float"
        elif expr.type == "STRING":
            return "String"
        elif expr.type == "IDENT":
            symbol = self.symbol_table_manager.lookup(expr.value)
            if symbol is None:
                raise Exception(f"Undefined variable '{expr.value}'")
            return symbol.data_type
        else:
            raise Exception(f"Unsupported expression type '{expr.type}' for type inference")

    def generate_loop_statement(self, loop_var, start_expr, end_expr, body_stmt, method_name):
        self.symbol_table_manager.define(
            loop_var,
            ST.SymbolType.VARIABLE,
            "int",
            Tokenizer.Token("IDENT", loop_var),
            slot=len(self.symbol_table_manager.table.symbols)
        )
        index = self.symbol_table_manager.lookup(loop_var).slot

        loop_id = self.get_new_label_id()
        self.generate_expression(start_expr)
        self.pop_symbol(f"local {index}")
        self.instructions.append(f"label LOOP_START{loop_id}")
        self.push_symbol(f"local {index}")
        self.generate_expression(end_expr)
        self.instructions.append("lt")
        self.instructions.append(f"if-goto LOOP_BODY{loop_id}")
        self.instructions.append(f"goto LOOP_END{loop_id}")
        self.instructions.append(f"label LOOP_BODY{loop_id}")
        self.generate_statmen(body_stmt.value)
        self.instructions.append(f"goto LOOP_START{loop_id}")
        self.instructions.append(f"label LOOP_END{loop_id}")

    def get_new_label_id(self):
        current_id = self.goto_count
        self.goto_count += 1
        return current_id






