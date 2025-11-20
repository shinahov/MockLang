from Tokenizer import Tokenizer, Token


def pretty_print(obj, indent=0):  # custom print function for debugging
    space = "    " * indent  # 4 spaces per indent level

    if isinstance(obj, list):
        print(space + "[")
        for item in obj:
            pretty_print(item, indent + 1)
        print(space + "]")

    elif isinstance(obj, tuple):
        print(space + "(")
        for item in obj:
            pretty_print(item, indent + 1)
        print(space + ")")

    elif hasattr(obj, "type") and hasattr(obj, "value"):  # Token
        if isinstance(obj.value, list):
            print(f"{space}Token({obj.type}, [")
            for val in obj.value:
                pretty_print(val, indent + 1)
            print(space + "])")
        else:
            print(f"{space}Token({obj.type}, {obj.value})")

    else:
        print(space + str(obj))

class Parser:
    def __init__(self, tokens):
        self.token = None
        self.tokens = tokens
        self.pos = 0
        self.programm = []

    def pop(self):
        self.token = self.tokens[self.pos]
        self.pos += 1
        # return token

    def parse(self):
        self.pop()
        assert self.token.type == "CLASS"
        self.pop()
        class_name = self.token
        assert class_name.type == "IDENT"
        self.programm.append(Token("CLASS_DEF", class_name.value))
        self.pop()
        token = self.token
        if token.type == "COLON":
            self.programm.append(Token("BODY", self.parse_body()))
        elif token.type == "LBRK":
            self.programm.append(Token("FIELDS", self.parse_fields()))
            self.pop()
            token = self.token
            # assert token.type == "COLON"
            self.programm.append(Token("BODY", self.parse_body()))
        # assert token.type == "END"
        return self.programm

    def parse_body(self):
        body = []
        while True:
            print("Parsing BODY, current token:", self.token)
            print("Current body:", body)
            self.pop() # consume ; maybe
            print("next token in body:", self.token)
            if self.token.type == "END":
                break
            if self.token.type == "CREATE":
                body.append(Token("CREATE_STMT", self.parse_create_stmt()))
                print("next token aftzer create", self.token)
                print("CREATE_STMT parsed:", body)
            if self.token.type == "SET":
                body.append(Token("SET_STMT", self.parse_set_stmt()))
                print("next token after set", self.token)
            if self.token.type == "PRINT":
                body.append(Token("PRINT_STMT", self.parse_print_stmt()))
            if self.token.type == "IF":
                body.append(Token("IF_STMT", self.parse_if_stmt()))
            if self.token.type == "FN":
                body.append(Token("FN_DEF", self.parse_fn_def()))
            if self.token.type == "IDENT":
                body.append(self.parse_ident())

            if self.token.type == "CLASS":
                raise NotImplementedError("Nested classes are not supported yet")
        return body

    def parse_fields(self):
        fields = []
        while True:
            self.pop()
            assert self.token.type == "IDENT"
            field_name = self.token.value
            self.pop()
            assert self.token.type == "COLON"
            self.pop()
            assert self.token.type.startswith("TYPE_")
            fields.append((field_name, self.token.value))
            self.pop()

            if self.token.type == "COMMA":
                continue
            elif self.token.type == "RBRK":
                break
            else:
                raise ValueError(f"Unexpected token {self.token}")
        return fields

    def parse_create_stmt(self):
        buffer = []
        if self.token.type != "CREATE":
            raise SyntaxError("CREATE_STMT must start with CREATE")
        self.pop()

        while True:
            #print("Parsing CREATE_STMT, current token:", self.token)
            if self.token.type == "SEMI":
                break
            if (self.token.type.startswith("TYPE_") or
                    self.token.type == "IDENT"):
                buffer.append(Token("TYPE", self.token.value))
                self.pop()
                if self.token.type == "IDENT":
                    buffer.append(Token("IDENT", self.token.value))
                    self.pop()
                    if self.token.type == "EQ":
                        buffer.append(Token("EQ", self.token.value))
                        self.pop()
                        if self.token.type == "IDENT" :
                            buffer.append(Token("IDENT", self.token.value))
                            self.pop()
                        else:
                            buffer.append(Token("EXPR", self.parse_expression()))
                        return buffer
                    elif self.token.type == "SEMI":
                        return buffer



    def parse_set_stmt(self):
        buffer = []
        if self.token.type != "SET":
            raise SyntaxError("SET_STMT must start with SET")
        self.pop()

        while True:
            #print("Parsing SET_STMT, current token:", self.token)
            if self.token.type == "SEMI":
                break
            if self.token.type == "TO":
                self.pop()
                buffer.append(Token("TO", self.parse_expression()))
                #self.pop()
                return buffer
            if self.token.type == "IDENT":
                buffer.append(Token("IDENT", self.token.value))
            self.pop()

        return buffer


    def parse_print_stmt(self):
        self.pop() # consume PRINT
        self.pop()  # consume LP
        expr = self.parse_expression()
        self.pop()  # consume SEMI
        return expr

    def parse_if_stmt(self):
        self.pop()  # consume IF
        self.pop()  # consume LP
        condition = self.parse_condition()
        if self.token.type != "LBRACE":
            raise SyntaxError("Expected '{' after IF condition")
        self.pop()  # consume LBRACE
        body = self.parse_if_else_body()
        self.pop()  # consume RBRACE
        if self.token.type == "ELSE":
            self.pop()  # consume ELSE
            if self.token.type != "LBRACE":
                raise SyntaxError("Expected '{' after ELSE")
            self.pop()  # consume LBRACE
            else_body = self.parse_if_else_body()
            self.pop()  # consume RBRACE
            return (Token("IF_ELSE_STMT", [condition, body, else_body]))
        return (Token("IF_STMT", [condition, body]))


    def parse_fn_def(self):
        pass

    def parse_ident(self):

        name = self.token.value
        #print("Parsing IDENT:", name)
        self.pop()
        if self.token.type == "DOT":
            self.pop()
            method_name = self.token
            assert method_name.type == "IDENT"
            self.pop()
            # print(self.programm)
            assert self.token.type == "LP"
            args = self.parse_args()
            self.pop()
            assert self.token.type == "RP"
            self.pop()
            assert self.token.type == "SEMI"
            return ("METHOD_CALL", self.token.value, f"{name}.{method_name.value}", args)
        elif self.token.type == "LP":
            #print("Parsing function/method call or definition for:", name)
            buffer = []
            while True:
                self.pop()
                #print("Current token in IDENT parsing:", self.token)
                if self.token.type in ["SEMI", "ARROW"]:
                    break
                buffer.append(self.token)
                #print("Buffer so far:", buffer)
            buffer.pop(0)  # remove RP

            if self.token.type == "SEMI":
                return ("FN_CALL", self.token.value, buffer)
            elif self.token.type == "ARROW":
                self.pop()
                return_type = self.parse_return_type()
                #print("Return type token:", return_type)
                assert self.token.type == "COLON"
                self.pop()
                body = self.parse_method_body()
                return ("METHOD_DEF", name, buffer, return_type, body)

    def parse_args(self):
        args = []
        while True:
            #print("Parsing argument, current token:", self.token)
            if self.token.type == "RP":
                break
            if self.token.type == "COMMA":
                continue
            args.append(self.token) # later parse expression
            self.pop()
        return args


    def parse_method_body(self):
        body = []
        while True:
            # self.pop()

            if self.token.type == "END":
                break
            if self.token.type == "CREATE":
                body.append(("CREATE_STMT", self.parse_create_stmt()))
            if self.token.type == "SET":
                body.append(("SET_STMT", self.parse_set_stmt()))
            if self.token.type == "PRINT":
                body.append(("PRINT_STMT", self.parse_print_stmt()))
            if self.token.type == "IF":
                body.append(("IF_STMT", self.parse_if_stmt()))
            if self.token.type == "IDENT":
                body.append(self.parse_ident())
            if self.token.type == "RETURN":
                #print("Parsing RETURN statement...")
                body.append(("RETURN_STMT", self.parse_return_stmt()))
                #print("RETURN parsed:", body)
                return body
            if self.token.type == "CLASS":
                raise NotImplementedError("Nested classes are not supported yet")
        return body

    def parse_return_stmt(self):
        self.pop()
        exprs = []
        cur = []

        while self.token.type != "SEMI":
            if self.token.type == "COMMA":
                if not cur:
                    raise SyntaxError("Empty expression vor ','")
                exprs.append(cur)
                cur = []
                self.pop()  # skipp ','
                continue

            if self.token.type == "IDENT":
                token = self.token
                chain = []
                self.pop()
                if self.token.type == "DOT":
                    #dot = self.token
                    self.pop() # skipp '.'
                    if self.token.type != "IDENT":
                        raise SyntaxError("Nach '.' wird IDENT erwartet")
                    name = self.token
                    self.pop()
                    if self.token.type == "LP":
                        self.pop()  # skipp '('
                        args = self.parse_args()
                        self.pop()  # skipp ')'
                        chain.extend([Token("CLASS_METHOD_CALL",
                                            [Token("CLASS", token.value),
                                             name,
                                             Token("ARGS", args)])])
                        #print("Parsed CLASS_METHOD_CALL:", chain)
                    else:
                        chain.extend([Token("ClASS", token.value), name])
                elif self.token.type == "LP":
                    self.pop()  # skipp '('
                    args = self.parse_args()
                    self.pop()  # skipp ')'
                    chain.append(Token("FN_CALL", [token, Token("ARGS", args)]))

                cur.extend(chain)
                continue


            cur.append(self.token)
            self.pop()

        # ;
        if cur:
            exprs.append(cur)
            #pretty_print(exprs)
        self.pop()  # ';' consumed
        return exprs

    def parse_return_type(self):
        buffer = []
        while True:
            # self.pop()
            if self.token.type == "COLON":
                if not buffer:
                    buffer.append(Token("TYPE_VOID", "void"))
                return buffer
            buffer.append(self.token)
            self.pop()

    def parse_expression(self):
        buffer = []
        while True:
            print("Parsing expression, current token:", self.token)
            if self.token.type in ["SEMI"]:
                print(" buffer ", buffer)
                break
            buffer.append(self.token)
            self.pop()
        return buffer

    def parse_condition(self):
        left = []
        right = []
        buffer = []
        comparator = None
        while True:
            #print("Parsing condition, current token:", self.token)
            if self.token.type == "LBRACE":
                # later parse expression for left and right
                return Token("CONDITION", [Token("LEFT", left), comparator, Token("RIGHT", right)])
            if self.token.type in Tokenizer.comperators:
                comparator = self.token
                self.pop()
                continue
            if comparator is None:
                left.append(self.token)
            else:
                right.append(self.token)
            self.pop()


        return buffer

    def parse_if_else_body(self):
        body = []
        while True:
            self.pop()
            if self.token.type == "RBRACE":
                break
            if self.token.type == "CREATE":
                body.append(("CREATE_STMT", self.parse_create_stmt()))
            if self.token.type == "SET":
                body.append(("SET_STMT", self.parse_set_stmt()))
            if self.token.type == "PRINT":
                body.append(("PRINT_STMT", self.parse_print_stmt()))
            if self.token.type == "IF":
                body.append(("IF_STMT", self.parse_if_stmt()))
            if self.token.type == "IDENT":
                body.append(self.parse_ident())
            if self.token.type == "CLASS":
                raise NotImplementedError("Nested classes are not supported yet")
        return body

