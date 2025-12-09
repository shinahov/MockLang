import os, sys, re
import Tokenizer
import Parser
import SymbolAnalyzer as SA
import Symbol_table as ST
import VMGenerator as VM

code = """class Ball [radius:int, x:int, y:int, speed:float]:
  create int q = 5;
  
  getBall() -> int, int, int:
    create int a = 11;
    some_func(55, a);
    return self.radius, a, self.q;
  end

  setBall(r:int, x:int) -> :
    set self.radius to r;
    set self.x to x;
  end 
  
  fn some_func(val:int, zahl:int) -> void:
    print(val);
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
    loop(int i,(0, 3)){
        print(i);
    }
    create int b;
    set b to 5;
    print(b);

    create Ball ball = Ball(5, 10, 3, 3.14);
    ball.setBall(6, 7);
    set z, a, c to ball.getBall();
    print(z);
    print(a);
    print(c);
    if(ball.radius =? 9){
      print(6);
    }
  END


end
"""

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
    tokens = Tokenizer.Tokenizer().tokenize(code)
    print("Tokens:", tokens)
    parser = Parser.Parser(tokens)
    programm = parser.parse()
    print("Programm:")
    Parser.pretty_print(programm)
    table = ST.SymbolTableManager()
    analyzer = SA.SymbolAnalyzer(table, programm)
    analyzer.analyze()
    print("Final Symbol Table:")

    print(table.table)
    vm_generator = VM.VMGenerator(table, programm)
    instructions = vm_generator.generate()
    print("Generated VM Instructions:")
    for instr in instructions:
        print(instr)


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

