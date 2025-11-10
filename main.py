import os, sys, re

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

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <file.xxx>")
        sys.exit(1)

    file_path = sys.argv[1]
    compiler = Compiler(file_path)

    try:
        compiler.compile()
    except Exception as e:
        print("Error:", e)
        sys.exit(1)

