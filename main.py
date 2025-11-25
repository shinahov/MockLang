import os, sys, re
import Tokenizer
import Parser
import SymbolAnalyzer as SA
import Symbol_table as ST

code = """class Ball [radius:int, x:int, y:int, speed:float]:
  create int z;
  set z to 10;
  create float pi = 3.14;
  print(pi);
  if(z > 5){
    print((z+5)*2);
  } else {
    print(0);
  }
  getRadius() -> int, int:
    return self.radius, self.x(y), someOtherThing();
  end

  setRadius(r:int, p:int) -> :
    set self.radius to r;
  end 


  fn main() -> void:
    create int b;
    set b to 5;
    print(b);

    create Ball ball = Ball(5, 10, 3, 3.14);
    ball.setRadius(6);
    print(ball.getRadius());
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
    #print("Tokens:", tokens)
    parser = Parser.Parser(tokens)
    programm = parser.parse()
    print("Programm:")
    Parser.pretty_print(programm)
    table = ST.SymbolTableManager()
    analyzer = SA.SymbolAnalyzer(table, programm)
    analyzer.analyze()


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

