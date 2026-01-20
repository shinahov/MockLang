from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Iterable, Optional


def is_main_function(func_name):
    try:
        name, main = func_name.split(".")
        return main == "main"
    except ValueError:
        return False




class ASMGenerator:
    def __init__(self, VM_instructions: List[str]):
        self.VM_instructions = VM_instructions
        self.asm_instructions: List[str] = []
        self.label_count = 0

    def generate(self) -> List[str]:
        self.generate_asm()
        return self.asm_instructions

    def generate_asm(self):
        self.make_header()
        self.translate_vm_instructions()

    def make_header(self):
        self.asm_instructions.append("default rel")
        self.asm_instructions.append("global main")
        self.asm_instructions.append("extern printf")
        self.write_ln()
        self.asm_instructions.append("section .data")
        self.asm_instructions.append('fmt_int db "%d", 10, 0')
        self.write_ln()
        self.add_bss_section()
        self.add_text_section()
        self.runtime_setup()

    def add_bss_section(self):
        self.asm_instructions.append("section .bss")
        self.asm_instructions.append("vm_stack: resq 1024")
        self.write_ln()

    def add_text_section(self):
        self.asm_instructions.append("section .text")
        self.write_ln()

    def runtime_setup(self):
        self.asm_instructions.append("main:")
        self.asm_instructions.append("    push rbp")
        self.asm_instructions.append("    mov rbp, rsp")
        self.asm_instructions.append("    lea r12, [vm_stack]")  # Initialize VM stack pointer
        self.asm_instructions.append("    mov r13, r12")  # lcl
        self.asm_instructions.append("    mov r14, r12")  # arg
        self.asm_instructions.append("    xor r15, r15")  # this = 0
        self.write_ln()
        self.asm_instructions.append("    jmp vm_start")

    def write_ln(self):
        self.asm_instructions.append("")

    def translate_vm_instructions(self):
        for instr in self.VM_instructions:
            parts = instr.split()
            cmd = parts[0]

            if cmd == "push":
                pass  # Implement push translation

            elif cmd == "pop":
                pass

            elif cmd == "add":
                pass

            elif cmd == "sub":
                pass

            elif cmd == "call":
                pass

            elif cmd == "return":
                pass

            elif cmd == "function":
                if len(parts) != 3:
                    raise ValueError(f"Invalid function instruction: {instr}")

                func_name = parts[1]
                nlocals = int(parts[2])
                if is_main_function(func_name):
                    self.asm_instructions.append("vm_start:")
                else:
                    self.write_fn_label(func_name)

    def write_fn_label(self, func_name):
        label = func_name.replace('.', '_')
        self.asm_instructions.append(f"{label}:")
