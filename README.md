# MockLang

MockLang is a small hobby programming language created to explore how compilers work — from lexing and parsing to semantic analysis and later code generation. It’s purely educational and not intended for production use.


## Requirements

- Python 3.10+
- `nasm`
- `gcc`
  - On Linux/WSL: install via your package manager
  - On Windows: you need NASM + a GCC toolchain (e.g., MinGW-w64) available in `PATH`


## Build / Run

### Compile a `.mcklng` file to an executable:
python3 mck.py path/to/program.mcklng
or:
python3 mck.py path/to/program.mcklng -name myprog
for custom executable name
-Output will be `myprog`, `myprog.o`, and `myprog.asm`

## Features
- Simple class and method system  
- Variables and scoped symbol tables  
- If/else control flow  
- Basic expressions  
- Extendable parser and analyzer  

## Example

```mocklang
class Person [name:String, age:int]:
  fn main() -> void:
    create Person p = Person("Alice", 30);
    print(p.name);
    print(p.age);
  end
end
```

## Variables:
```` mocklang
create int a = 10;
create float pi = 3.14;
create String text = "Hello";
````

## Assignments:
```` mocklang
set a to 55;
set text to "World";
````

## Printing:
```` mocklang
print(a);
print(text);
````

## If/Else:
```` mocklang
create int a = 10;

if(a > 5){
  print(1);
} else {
  print(0);
}
````

## Equality:
```` mocklang
if(a =? 5){
  print(100);
} else {
  print(200);
}
````

## Loops:
```` mocklang
loop(i, (0; 5;)){
  print(i);
  set i to (i + 1);
}
````

## Functions/Methods:
```` mocklang
class Test :
  add(a:int, b:int) -> int:
    return a + b;
  end

  fn main() -> void:
    print(add(10, 20));
  end
end
````

## Multi return
````mocklang
class Test :
  fn pair() -> int, int:
    create int a = 10;
    create int b = 20;
    return a, b;
  end

  fn main() -> void:
    create int x;
    create int y;
    set x, y to pair();
    print(x);
    print(y);
  end
end
````

## Self
````mocklang
class Test [zahl:int]:
  get_zahl() -> int:
    return self.zahl;
  end

  fn main() -> void:
    create Test test = Test(123);
    create int zahl;
    set zahl to test.get_zahl();
    print(zahl);
  end
end

````




## Project Structure
- **Tokenizer.py** – Lexer  
- **Parser.py** – AST builder  
- **SymbolAnalyzer.py** – Scope and type analysis  
- **Symbol_table.py** – Symbol table manager  
- **main.py** – Driver / example  
- **VMGenerator.py** – VM code generator
- **ASMGenerator.py** – Assembly code generator
- **mck.py** – CLI interface

## Current Stage
- VM → Assembly translator is implemented (ASM output + executable build via NASM/GCC).

## Future Work
- Arrays
- More complex statements / language constructs
- Bug fixes (there are still some known issues)

