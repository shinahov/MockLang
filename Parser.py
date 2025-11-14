from Tokenizer import Tokenizer, Token


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
        self.programm.append(("CLASS_DEF", class_name.value))
        self.pop()
        token = self.token
        if token.type == "COLON":
            self.programm.append(("BODY", self.parse_body()))
        elif token.type == "LBRK":
            self.programm.append(("FIELDS", self.parse_fields()))
            self.pop()
            token = self.token
            # assert token.type == "COLON"
            self.programm.append(("BODY", self.parse_body()))
        # assert token.type == "END"
        return self.programm

    def parse_body(self):
        body = []
        while True:
            self.pop()
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
            if self.token.type == "FN":
                body.append(("FN_DEF", self.parse_fn_def()))
            if self.token.type == "IDENT":
                print("Parsing IDENT in body... ", self.token)
                body.append(self.parse_ident())
                print("body so far:", body)
                print(self.programm)
                return
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
        pass

    def parse_set_stmt(self):
        pass

    def parse_print_stmt(self):
        pass

    def parse_if_stmt(self):
        pass

    def parse_fn_def(self):
        pass

    def parse_ident(self):

        name = self.token.value
        print("Parsing IDENT:", name)
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
            print("Parsing function/method call or definition for:", name)
            buffer = []
            while True:
                self.pop()
                print("Current token in IDENT parsing:", self.token)
                if self.token.type in ["SEMI", "ARROW"]:
                    break
                buffer.append(self.token)
                print("Buffer so far:", buffer)
            buffer.pop(0)  # remove RP

            if self.token.type == "SEMI":
                return ("FN_CALL", self.token.value, buffer)
            elif self.token.type == "ARROW":
                self.pop()
                return_type = self.parse_return_type()
                print("Return type token:", return_type)
                # assert return_type[-1].type.startswith("TYPE_")
                # self.pop()
                # print("Current token before COLON check:", self.token)
                assert self.token.type == "COLON"
                self.pop()
                body = self.parse_method_body()
                return ("METHOD_DEF", name, buffer, return_type, body)

    def parse_args(self):
        pass

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
                print("Parsing RETURN statement...")
                body.append(("RETURN_STMT", self.parse_return_stmt()))
                print("RETURN parsed:", body)
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
                                            [Token("CLASS", token.value), name, Token("ARGS", args)])])
                    else:
                        chain.extend([Token("ClASS", token.value), name])
                    #self.pop()
                cur.extend(chain)
                continue


            cur.append(self.token)
            self.pop()

        # ;
        if cur:
            exprs.append(cur)
        self.pop()  # ';' konsumieren
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
