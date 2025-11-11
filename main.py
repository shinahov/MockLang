import os, sys, re
import Tokenizer
import Parser

code = """class Ball [radius:int, x:int, y:int, speed:float]:
  getRadius() -> int:
    return self.radius;
  end

  setRadius(r:int):
    set self.radius to r;
  end 
end

fn main() -> void:
  create int b;
  set b to 5;
  print(b);

  create Ball ball = Ball(5, 10, 3, 3.14);
  ball.setRadius(6);
  print(ball.getRadius());
  if(ball.radius =? 6){
    print(6);
  }


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
    parser = Parser.Parser(tokens)
    programm = parser.parse()
    print("Programm:", programm)


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

