import sys
import subprocess
from pathlib import Path

import Tokenizer
import Parser
import SymbolAnalyzer as SA
import Symbol_table as ST
import VMGenerator as VM
import ASMGenerator as ASM



def usage():
    print("Usage: python3 mck.py <file.mcklng> [-asm] [-name <output_name>]")
    sys.exit(1)


def compile_to_asm(source_code: str) -> list[str]:
    tokens = Tokenizer.Tokenizer().tokenize(source_code)
    parser = Parser.Parser(tokens)
    program = parser.parse()

    symbol_table_manager = ST.SymbolTableManager()
    symbol_analyzer = SA.SymbolAnalyzer(symbol_table_manager, program)
    symbol_analyzer.analyze()

    vm_generator = VM.VMGenerator(symbol_table_manager, program)
    instructions = vm_generator.generate()

    asm_generator = ASM.ASMGenerator(instructions)
    asm_instructions = asm_generator.generate()

    return asm_instructions

def main():
    if len(sys.argv) < 2:
        usage()

    src_path = Path(sys.argv[1]).expanduser().resolve()
    if src_path.suffix != ".mcklng":
        print("file must end with .mcklng")
        sys.exit(1)
    if not src_path.exists():
        print(f"file not found: {src_path}")
        sys.exit(1)

    name = None
    if "-name" in sys.argv:
        name_index = sys.argv.index("-name") + 1
        if name_index < len(sys.argv):
            name = sys.argv[name_index]
        else:
            print("name not specified after -name")
            sys.exit(1)
    else:
        name = src_path.stem

    out_dir = src_path.parent
    asm_out_path = out_dir / f"{name}.asm"
    obj_out_path = out_dir / f"{name}.o"
    exe_out_path = out_dir / name

    code = src_path.read_text(encoding="utf-8")
    asm_instructions = compile_to_asm(code)


    asm_out_path.write_text("\n".join(asm_instructions), encoding="utf-8")

    subprocess.run(
        ["nasm", "-f", "elf64", str(asm_out_path), "-o", str(obj_out_path)], check=True)
    subprocess.run(
        ["gcc", "-no-pie", str(obj_out_path), "-o", str(exe_out_path)], check=True)

    print(f"Executable built at: {exe_out_path}")

if __name__ == "__main__":
    main()





