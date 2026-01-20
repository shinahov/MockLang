from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Iterable, Optional

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

    def make_header(self):
        self.asm_instructions.append("default rel")
        self.asm_instructions.append("global main")
        self.asm_instructions.append("extern printf")
        self.write_ln()
        self.asm_instructions.append("section .data")
        self.asm_instructions.append('fmt_int db "%d", 10, 0')
        self.write_ln()

    def write_ln(self):
        self.asm_instructions.append("")