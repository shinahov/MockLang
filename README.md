# MockLang

MockLang is a small hobby programming language created to explore how compilers work — from lexing and parsing to semantic analysis and later code generation. It’s purely educational and not intended for production use.

## Features
- Simple class and method system  
- Variables and scoped symbol tables  
- If/else control flow  
- Basic expressions  
- Extendable parser and analyzer  

## Example

```mocklang
class Ball [radius:int, x:int, y:int, speed:float]:
  create int z;
  set z to 10;
  print(z);

  getRadius() -> int:
    return self.radius;
  end

  fn main() -> void:
    create int b = 5;
    print(b);
  END
end
```

## Project Structure
- **Tokenizer.py** – Lexer  
- **Parser.py** – AST builder  
- **SymbolAnalyzer.py** – Scope and type analysis  
- **Symbol_table.py** – Symbol table manager  
- **main.py** – Driver / example  

## Current Stage
- Finalizing symbol table logic

### Next steps
- Write VM code parser  
- Write assembler code parser  
- Implement VM → assembly translation  

MockLang is ideal for learning and experimenting with compiler architecture.

