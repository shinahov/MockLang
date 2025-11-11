from Tokenizer import Tokenizer, Token
class Parser:
    def __init__(self, tokens):
        self.token = None
        self.tokens = tokens
        self.pos = 0
        self.programm = []

    def pop(self):
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def parse(self):
        token = self.pop()
        assert token.type == "CLASS"
        class_name = self.pop()
        assert class_name.type == "IDENT"
        self.programm.append(("CLASS_DEF", class_name.value))
        token = self.pop()
        if token.type == "COLON":
            self.programm.append(("BODY", self.parse_body()))
        elif token.type == "LBRK":
            self.programm.append(("FIELDS", self.parse_fields()))
            token = self.pop()
            #assert token.type == "COLON"
            self.programm.append(("BODY", self.parse_body()))
        #assert token.type == "END"
        return self.programm

    def parse_body(self):
        body = []
        while True:
            self.token = self.pop()
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
                print("Parsing IDENT in body... " , self.token)
                body.append(self.parse_ident())
                print(self.programm)
                return 
            if self.token.type == "CLASS":
                raise NotImplementedError("Nested classes are not supported yet")
        return body

    def parse_fields(self):
        fields = []
        while True:
            field_name = self.pop()
            assert field_name.type == "IDENT"
            colon = self.pop()
            assert colon.type == "COLON"
            field_type = self.pop()
            assert field_type.type.startswith("TYPE_")
            fields.append((field_name.value, field_type.value))
            token = self.pop()
            if token.type == "COMMA":
                continue
            elif token.type == "RBRK":
                break
            else:
                raise ValueError(f"Unexpected token {token}")
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
        print("Parsing ident...")
        #ident_name = self.pop()
        print("Ident name:", self.token.value)
        self.token = self.pop()
        if self.token.type == "DOT":
            method_name = self.pop()
            assert method_name.type == "IDENT"
            lp = self.pop()
            print(self.programm)
            assert lp.type == "LP"
            args = self.parse_args()
            rp = self.pop()
            assert rp.type == "RP"
            semi = self.pop()
            assert semi.type == "SEMI"
            return ("METHOD_CALL", self.token.value, method_name.value, args)
        elif self.token.type == "LP":
            buffer = []
            while self.token.type != "RP":
                self.token = self.pop()
                buffer.append(self.token)
            self.token = self.pop()
            if self.token.type == "SEMI":
                return ("FN_CALL", self.token.value, buffer)
            elif self.token.type == "ARROW":
                return_type = self.pop()
                assert return_type.type.startswith("TYPE_")
                colon = self.pop()
                assert colon.type == "COLON"
                body = self.parse_method_body()
                return ("METHOD_DEF", self.token.value, buffer, return_type.value, body)
                
        
    def parse_args(self):
        pass

    def parse_method_body(self):
        pass



