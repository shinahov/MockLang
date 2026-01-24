import os, sys, re
import Tokenizer
import Parser
import SymbolAnalyzer as SA
import Symbol_table as ST
import VMGenerator as VM
import ASMGenerator as ASM

output_path = "/home/ibrahim_shinahov/Desktop/vmstack_add.asm"

code = """class Ball [radius:int, x:int, y:int, speed:float]:
  create int q = 5;
  
  getBall() -> int, int, int:
    create int a = 11;
    some_func(55, a);
    return self.radius, a, self.q;
  end

  setBall(r:int, x:int) -> :
    set r to 55;
    set self.radius to r;
    set self.x to x;
  end 
  
  fn some_func(val:int, zahl:int) -> int, int:
    create Ball ball1 = Ball(5, 10, 3, 3.14);
    print(val);
    return ball1.x, val;
  end


  fn main() -> void:
    create int z;
    set z to 10;
    create int a;
    create int c;
    create float pi = 3.14;
    print(pi);
    create String text = "Hello World!";
    print(text);
    if(z > 5){
      print((z+5)*2);
    } else {
      print(0);
    }
    loop(i, (0; 3;)){
        print(i);
        set i to (i + 1);
    }
    create int b;
    set b to 5;
    print(b);

    create Ball ball = Ball(5, 10, 3, 3.14);
    ball.setBall(6, 7);
    set z, a, c to ball.getBall();
    set a to ball.radius;
    print(z);
    print(a);
    print(c);
    if(ball.radius =? 9){
      print(6);
    }
  END


end
"""

code_simple = """class Test :
    fn main() -> void:
    create int a = 10;
    create int b = 50;
    print(a + b);
    end
end
"""

code_func_call = """class Test :
    fn function_print(zahl: int) -> :
       create int c;
       set c to zahl;
       print(c);
    end
       
    fn main() -> void:
       create int a = 10;
       create int b = 50;
       function_print(a);
       function_print(b);
    end
end
"""

code_multi_return = """class Test :
    fn multi_return() -> int, int:
       create int a = 10;
       create int b = 20;
       return a, b;
    end
       
    fn main() -> void:
       create int x;
       create int y;
       set x, y to multi_return();
       print(x);
       print(y);
    end
end
"""

code_if_else = """class Test :
    fn main() -> void:
       create int a = 10;
       if(a > 5){
          print(1);
       } else {
          print(0);
       }
    end
end
"""

code_simple_if_else = """class Test :
    fn main() -> void:
       create int a = 3;
       if(a =? 5){
          print(100);
       } else {
          print(200);
       }
    end
end
"""

code_simple_loop = """class Test :
    fn main() -> void:
       loop(i, (0; 5;)){
          print(i);
          set i to (i + 1);
       }
    end
end
"""

code_string_print = """class Test :
    fn main() -> void:
       create String text = "Hello, Compiler!";   
       print(text);
    end
end
"""

code_obj_field_access = """class Person [name:String, age:int]:
    fn main() -> void:
         create Person p = Person("Alice", 30);
            print(p.name);
            print(p.age);
    end
end
"""



fin_code = code_obj_field_access

class Compiler:
    def __init__(self, path):
        self.path = path

    def compile(self):
        if not self.path.endswith('.xxx'):
            raise ValueError("file must end with .xxx")
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"file {self.path} does not exist")

        print("compiling", self.path)

        # Compilation logic goes here


def let_test():
    tokens = Tokenizer.Tokenizer().tokenize(fin_code)
    #print("Tokens:", tokens)
    parser = Parser.Parser(tokens)
    programm = parser.parse()
    print("Programm:")
    Parser.pretty_print(programm)
    table = ST.SymbolTableManager()
    analyzer = SA.SymbolAnalyzer(table, programm)
    analyzer.analyze()
    #print("Final Symbol Table:")

    #print(table.dump())  # nur scopes + symbols
    #print(table.dump(show_node=True))  # zusätzlich node-typen

    vm_generator = VM.VMGenerator(table, programm)
    instructions = vm_generator.generate()
    print("Generated VM Instructions:")
    for instr in instructions:
        print(instr)
    print("")
    print("_______________________________")

    asm_generator = ASM.ASMGenerator(instructions)
    asm_instructions = asm_generator.generate()
    print("Generated ASM Instructions:")
    for instr in asm_instructions:
        print(instr)
    with open(r"C:\Users\ibrahim shinahov\Desktop\vmstack_add.asm", "w") as f:
        f.write("\n".join(asm_instructions))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        #print("Usage: python main.py <file.xxx>")
        let_test()
        sys.exit(1)

    file_path = sys.argv[1]
    compiler = Compiler(file_path)

    try:
        compiler.compile()
    except Exception as e:
        print("Error:", e)
        sys.exit(1)

