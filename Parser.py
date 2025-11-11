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
        pass

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



