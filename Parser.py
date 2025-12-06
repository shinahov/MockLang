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


    elif hasattr(obj, "type") and hasattr(obj, "value"):

        if isinstance(obj.value, list):

            print(f"{space}Token({obj.type}, [")

            for val in obj.value:
                pretty_print(val, indent + 1)

            print(space + "])")

        else:

            print(f"{space}Token({obj.type},")

            pretty_print(obj.value, indent + 1)

            print(space + ")")


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
        assert class_name.type == "CLASS_NAME"
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
            self.pop() # consume ; maybe
            if self.token.type == "END":
                break
            if self.token.type == "CREATE":
                body.append(Token("CREATE_STMT", self.parse_create_stmt()))
            if self.token.type == "SET":
                body.append(Token("SET_STMT", self.parse_set_stmt()))
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
        self.pop() # consume CREATE

        while True:
            if self.token.type == "SEMI":
                break
            if (self.token.type.startswith("TYPE_") or
                    self.token.type == "IDENT") or self.token.type == "CLASS_NAME":
                buffer.append(Token("TYPE", self.token.value))
                self.pop()
                if self.token.type == "IDENT":
                    buffer.append(Token("IDENT", self.token.value))
                    self.pop()
                    if self.token.type == "EQ":
                        buffer.append(Token("EQ", self.token.value))
                        self.pop()
                        if self.token.type == "IDENT"  :
                            buffer.append(Token("IDENT", self.token.value))
                            self.pop()
                        elif self.token.type == "CLASS_NAME":
                            buffer.append(Token("CLASS_NAME", self.token.value))
                            self.pop() # consume CLASS_NAME
                            assert self.token.type == "LP"
                            self.pop() # consume LP
                            args = self.parse_args()
                            buffer.append(Token("ARGS", args))
                            self.pop() # consume RP
                            assert self.token.type == "SEMI"

                        else:
                            buffer.append(self.parse_expression())
                        return buffer
                    elif self.token.type == "SEMI":
                        pretty_print(buffer)
                        return buffer



    def parse_set_stmt(self):
        buffer = []
        if self.token.type != "SET":
            raise SyntaxError("SET_STMT must start with SET")
        self.pop()
        if self.token.type == "SELF" or self.token.type == "IDENT":
            buffer.append(Token(self.token.type, self.token.value))
            self.pop() # consume SELF or IDENT
            if self.token.type == "DOT":
                self.pop() # consume DOT
                if self.token.type != "IDENT":
                    raise SyntaxError("Expected IDENT after 'self.'")
                buffer.append(Token("IDENT", self.token.value))
                self.pop() # consume IDENT
                if self.token.type == "COMMA":
                    self.pop() # consume COMMA
                    while self.token.type == "IDENT":
                        buffer.append(Token("IDENT", self.token.value))
                        self.pop() # consume IDENT
                        if self.token.type == "COMMA":
                            self.pop() # consume COMMA
                if self.token.type == "TO":
                    self.pop() # consume TO
                    buffer.append(Token("TO", self.parse_expression()))
            elif self.token.type == "TO":
                self.pop() # consume TO
                buffer.append(Token("TO", self.parse_expression()))
            elif self.token.type == "COMMA":
                self.pop() # consume COMMA
                while self.token.type == "IDENT":
                    buffer.append(Token("IDENT", self.token.value))
                    self.pop() # consume IDENT
                    if self.token.type == "COMMA":
                        self.pop() # consume COMMA
                    if self.token.type == "TO":
                        self.pop() # consume TO
                        buffer.append(Token("TO", self.parse_expression()))

        print("SET_STMT parsed:", buffer)
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
            raise SyntaxError("Expected '{' after IF condition but got " + self.token.type)
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
        self.pop() # consume FN
        return self.parse_ident()

    def parse_ident(self):
        name = self.token.value
        self.pop()
        if self.token.type == "DOT":
            self.pop()
            method_name = self.token
            assert method_name.type == "IDENT"
            self.pop()
            assert self.token.type == "LP"
            self.pop() # consume (
            args = self.parse_args()
            if self.token.type != "RP":
                print("Expected ')' after method call arguments but got " , self.token.type)
            assert self.token.type == "RP"
            self.pop() # consume )
            assert self.token.type == "SEMI"
            return (Token("CLASS_METHOD_CALL", [Token("CLASS", name),
                                                method_name,
                                                Token("ARGS", args)]))
        elif self.token.type == "LP":
            self.pop() # consume (
            buffer = self.parse_args()
            self.pop() # consume )


            if self.token.type == "SEMI":

                return (Token("FN_CALL", [Token("NAME", name),
                                          Token("ARGS", buffer)]))
            elif self.token.type == "ARROW":
                self.pop() # consume ->
                return_type = self.parse_return_type()
                assert self.token.type == "COLON"
                self.pop() # consume :
                print("first token in method body:", self.token)
                body = self.parse_method_body()
                return (Token("METHOD_DEF",
                              [Token("NAME", name),
                               Token("ARGS", buffer),
                               Token("RETURN_TYPE", return_type),
                               Token("BODY", body)]))

    def parse_args(self):
        args = []
        while True:
            if self.token.type == "RP":
                break
            if self.token.type == "COMMA":
                self.pop() # skipp ,
                continue
            args.append(self.token) # later parse expression
            self.pop()
        return args


    def parse_method_body(self):
        body = []
        while True:
            if self.token.type == "END":
                break
            if self.token.type == "CREATE":
                body.append(Token("CREATE_STMT", self.parse_create_stmt()))
            if self.token.type == "SET":
                body.append(Token("SET_STMT", self.parse_set_stmt()))
            if self.token.type == "PRINT":
                body.append(Token("PRINT_STMT", self.parse_print_stmt()))
            if self.token.type == "IF":
                body.append(Token("IF_STMT", self.parse_if_stmt()))
            if self.token.type == "IDENT":
                body.append(self.parse_ident())
            if self.token.type == "RETURN":
                body.append(Token("RETURN_STMT", self.parse_return_stmt()))
                return body
            if self.token.type == "SEMI":
                self.pop()
            if self.token.type == "LOOP":
                while self.token.type != "RBRACE":
                    print(self.token)
                    self.pop()
                self.pop()  # consume RBRACE
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

            if self.token.type == "IDENT" or self.token.type == "SELF":
                token = self.token
                chain = []
                self.pop() # skipp self or ident
                if self.token.type == "DOT":
                    #print("HERE in return stmt parsing CLASS_METHOD_CALL with DOT :", token )
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
        self.pop()  # ';' consumed
        return exprs

    def parse_return_type(self):
        buffer = []
        while True:
            if self.token.type == "COLON":
                if not buffer:
                    buffer.append(Token("TYPE_VOID", "void"))
                return buffer
            if self.token.type == "COMMA":
                self.pop()
                continue
            buffer.append(self.token)
            self.pop()

    def parse_expression(self):
        buffer = []
        while True:
            if self.token.type == "SEMI" or self.token.type == "RP":
                break

            if self.token.type == "LP":
                self.pop()  # '('
                subexpr = Token("TERM", self.parse_expression())# rekursiv
                buffer.append(subexpr)
                assert self.token.type == "RP"
                self.pop()  # ')'
                continue
            if self.token.type in Tokenizer.comperators:
                buffer.append(Token("COMPERATOR", self.token.value))
                self.pop()
                continue
            if self.token.type in Tokenizer.operators:
                buffer.append(Token("OPERATOR", self.token.value))
                self.pop()
                continue

            buffer.append(self.token)
            self.pop()

        return Token("EXPR", buffer)

    def parse_condition(self):
        condition = self.parse_expression()
        self.pop() # consume RP
        if self.token.type != "LBRACE":
            raise SyntaxError("Expected '{' after IF condition but got " + self.token.type)
        return condition


    def parse_if_else_body(self):
        body = []
        while True:
            if self.token.type == "RBRACE":
                break
            if self.token.type == "CREATE":
                body.append(Token("CREATE_STMT", self.parse_create_stmt()))
            if self.token.type == "SET":
                body.append(Token("SET_STMT", self.parse_set_stmt()))
            if self.token.type == "PRINT":
                body.append(Token("PRINT_STMT", self.parse_print_stmt()))
            if self.token.type == "IF":
                body.append(Token("IF_STMT", self.parse_if_stmt()))
            if self.token.type == "IDENT":
                body.append(self.parse_ident())
            if self.token.type == "RETURN":
                body.append(Token("RETURN_STMT", self.parse_return_stmt()))
            if self.token.type == "SEMI":
                self.pop()
            if self.token.type == "CLASS":
                raise NotImplementedError("Nested classes are not supported yet")
        return body

