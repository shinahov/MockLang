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
        self.terminate_program()

    def make_header(self):
        self.asm_instructions.append("default rel")
        self.create_alias()
        self.write_ln()
        self.asm_instructions.append("global main")
        # Mem alloc stubben
        self.asm_instructions.append("global Memory_alloc")
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
        self.stubb_mem_alloc()
        self.asm_instructions.append("main:")
        self.asm_instructions.append("    push rbp")
        self.asm_instructions.append("    mov rbp, rsp")
        self.asm_instructions.append("    lea SP, [vm_stack]")  # Initialize VM stack pointer
        self.asm_instructions.append("    mov LCL, SP")  # lcl
        self.asm_instructions.append("    mov ARG, SP")  # arg
        self.asm_instructions.append("    xor THIS, THIS")  # this = 0
        self.write_ln()
        self.asm_instructions.append("    jmp vm_start")

    def write_ln(self):
        self.asm_instructions.append("")

    def translate_vm_instructions(self):
        for instr in self.VM_instructions:
            parts = instr.split()
            cmd = parts[0]

            if cmd == "push":
                self.push(parts)

            elif cmd == "pop":
                self.pop(parts)

            elif cmd == "add":
                self.asm_instructions.append("    sub SP, 8  ; decrement stack pointer")
                self.asm_instructions.append("    mov rbx, [SP]  ; pop y")
                self.asm_instructions.append("    sub SP, 8  ; decrement stack pointer")
                self.asm_instructions.append("    mov rax, [SP]  ; pop x")
                self.asm_instructions.append("    add rax, rbx    ; x + y")
                self.push_rax()

            elif cmd == "sub":
                self.asm_instructions.append("    sub SP, 8  ; decrement stack pointer")
                self.asm_instructions.append("    mov rax, [SP]  ; pop y")
                self.asm_instructions.append("    sub SP, 8  ; decrement stack pointer")
                self.asm_instructions.append("    mov rbx, [SP]  ; pop x")
                self.asm_instructions.append("    sub rbx, rax    ; x - y")
                self.push_rbx()

            elif cmd == "call":
                if len(parts) != 3:
                    raise ValueError(f"Invalid call instruction: {instr}")

                func_name = parts[1]
                nargs = int(parts[2])

                if func_name == "print.int" and nargs == 1:
                    self.write_print_int(parts)
                else:
                    self.call_function(func_name, nargs)

            elif cmd == "return":
                count = int(parts[1])
                #print(f"Return with count {count} not implemented yet.")
                self.write_return(count)

            elif cmd == "function":
                if len(parts) != 3:
                    raise ValueError(f"Invalid function instruction: {instr}")

                func_name = parts[1]
                nlocals = int(parts[2])
                self.write_fn_label(func_name, nlocals)

    def write_fn_label(self, func_name, nlocals):
        if is_main_function(func_name):
            self.asm_instructions.append("vm_start:")
        else:
            self.asm_instructions.append(f"{func_name}:")
        self.create_stack_frame(nlocals)

    def push(self, parts):
        if len(parts) != 3:
            raise ValueError(f"Invalid push instruction: {' '.join(parts)}")

        segment = parts[1]
        index = parts[2]

        if segment == "constant":
            self.push_constant(index)
        elif segment == "local":
            self.push_local(index)
        elif segment == "argument":
            self.push_argument(index)
        elif segment == "this":
            self.push_this(index)
        elif segment == "pointer":
            self.push_this(index)  # pointer 0 is this
        elif segment == "that":
            pass # dont have that segment implemented yet
        else:
            raise ValueError(f"Unknown segment in push instruction: {segment}")

    def push_constant(self, index):
        self.asm_instructions.append(f"    mov rax, {index}")
        self.asm_instructions.append(f"    mov [SP], rax")
        self.asm_instructions.append(f"    add SP, 8  ; increment stack pointer")
        self.write_ln()

    def push_local(self, index):
        self.asm_instructions.append(f"    mov rax, [LCL + {int(index) * 8}]")
        self.asm_instructions.append(f"    mov [SP], rax")
        self.asm_instructions.append(f"    add SP, 8  ; increment stack pointer")
        self.write_ln()

    def push_argument(self, index):
        self.asm_instructions.append(f"    mov rax, [ARG + {int(index) * 8}]")
        self.asm_instructions.append(f"    mov [SP], rax")
        self.asm_instructions.append(f"    add SP, 8  ; increment stack pointer")
        self.write_ln()

    def push_this(self, index):
        self.asm_instructions.append(f"    mov rax, [THIS + {int(index) * 8}]")
        self.asm_instructions.append(f"    mov [SP], rax")
        self.asm_instructions.append(f"    add SP, 8  ; increment stack pointer")
        self.write_ln()

    def pop(self, parts):
        if len(parts) != 3:
            raise ValueError(f"Invalid pop instruction: {' '.join(parts)}")

        segment = parts[1]
        index = parts[2]

        if segment == "local":
            self.pop_local(index)
        elif segment == "argument":
            self.pop_argument(index)
        elif segment == "this":
            self.pop_this(index)
        elif segment == "that":
            pass

    def pop_local(self, index):
        self.asm_instructions.append(f"    sub SP, 8  ; decrement stack pointer")
        self.asm_instructions.append(f"    mov rax, [SP]")
        self.asm_instructions.append(f"    mov [LCL + {int(index) * 8}], rax")
        self.write_ln()

    def pop_argument(self, index):
        self.asm_instructions.append(f"    sub SP, 8  ; decrement stack pointer")
        self.asm_instructions.append(f"    mov rax, [SP]")
        self.asm_instructions.append(f"    mov [ARG + {int(index) * 8}], rax")
        self.write_ln()

    def pop_this(self, index):
        self.asm_instructions.append(f"    sub SP, 8  ; decrement stack pointer")
        self.asm_instructions.append(f"    mov rax, [SP]")
        self.asm_instructions.append(f"    mov [THIS + {int(index) * 8}], rax")
        self.write_ln()

    def push_rax(self):
        self.asm_instructions.append(f"    mov [SP], rax")
        self.asm_instructions.append(f"    add SP, 8  ; increment stack pointer")
        self.write_ln()

    def write_print_int(self, parts):
        self.pop_rax()
        self.asm_instructions.append("    mov rsi, rax")
        self.asm_instructions.append("    lea rdi, [fmt_int]")
        self.asm_instructions.append("    xor rax, rax")
        self.asm_instructions.append("    call printf")

    def pop_rax(self):
        self.asm_instructions.append("    sub SP, 8  ; decrement stack pointer")
        self.asm_instructions.append("    mov rax , [SP]  ; pop value into rax")

    def write_return(self, count: int):

        if count < 0:
            raise ValueError("count must be >= 0")

        loop_label = f"RET_COPY_LOOP{self.label_count}"
        done_label = f"RET_COPY_DONE{self.label_count}"
        self.label_count += 1

        # Save frame and return address (your layout: RET at [FRAME - 32])
        self.asm_instructions.append("    mov FRAME, LCL")
        self.asm_instructions.append("    mov RET, [FRAME - 32]")

        # Save source/destination bases before restoring registers
        # rax = address of local segment base (source of return values)
        # TEMP = address of argument segment base (destination in caller)
        self.asm_instructions.append("    mov rax, LCL")
        self.asm_instructions.append("    mov TEMP, ARG")

        # Restore saved registers from the call frame (your layout)
        self.asm_instructions.append("    mov THIS, [FRAME - 8]")
        self.asm_instructions.append("    mov ARG,  [FRAME - 16]")
        self.asm_instructions.append("    mov LCL,  [FRAME - 24]")

        # Copy `count` qwords: [rax + i*8] -> [TEMP + i*8]
        self.asm_instructions.append(f"    mov rcx, {count}")
        self.asm_instructions.append(f"{loop_label}:")
        self.asm_instructions.append("    test rcx, rcx")
        self.asm_instructions.append(f"    jz {done_label}")
        self.asm_instructions.append("    dec rcx")
        self.asm_instructions.append("    mov rbx, [rax + rcx*8]")
        self.asm_instructions.append("    mov [TEMP + rcx*8], rbx")
        self.asm_instructions.append(f"    jmp {loop_label}")

        self.asm_instructions.append(f"{done_label}:")

        # Set SP for caller: SP = (old ARG base) + count*8
        self.asm_instructions.append(f"    lea SP, [TEMP + {count * 8}]")

        # Jump back
        self.asm_instructions.append("    jmp RET")
        self.write_ln()

    def terminate_program(self):
        self.asm_instructions.append("    mov eax, 0")
        self.asm_instructions.append("    leave")
        self.asm_instructions.append("    ret")

    def push_rbx(self):
        self.asm_instructions.append(f"    mov [SP], rbx")
        self.asm_instructions.append(f"    add SP, 8  ; increment stack pointer")
        self.write_ln()

    def create_stack_frame(self, nlocals: int):
        self.push_0_nlocals(nlocals)
        self.write_ln()

    def push_0_nlocals(self, nlocals):
        for _ in range(nlocals):
            self.asm_instructions.append("    mov qword [SP], 0")
            self.asm_instructions.append("    add SP, 8  ; increment stack pointer")

    def create_alias(self):
        self.asm_instructions.append("; Aliases")
        self.asm_instructions.append("%define SP    r12")
        self.asm_instructions.append("%define LCL   r13")
        self.asm_instructions.append("%define ARG   r14")
        self.asm_instructions.append("%define THIS  r15")
        self.asm_instructions.append("%define FRAME r10")
        self.asm_instructions.append("%define RET   r11")
        self.asm_instructions.append("%define TEMP  r9")
        self.write_ln()

    def call_function(self, func_name, nargs):
        return_label = f"RET_LABEL{self.label_count}"
        self.label_count += 1

        # Push return address
        self.asm_instructions.append(f"    lea RET, [rel {return_label}]")
        self.asm_instructions.append("    mov [SP], RET")
        self.asm_instructions.append("    add SP, 8  ; increment stack pointer")

        # Save LCL, ARG, THIS
        self.asm_instructions.append("    mov [SP], LCL")
        self.asm_instructions.append("    add SP, 8  ; increment stack pointer")
        self.asm_instructions.append("    mov [SP], ARG")
        self.asm_instructions.append("    add SP, 8  ; increment stack pointer")
        self.asm_instructions.append("    mov [SP], THIS")
        self.asm_instructions.append("    add SP, 8  ; increment stack pointer")

        # Reposition ARG
        self.asm_instructions.append("    mov TEMP, SP")
        self.asm_instructions.append(f"    sub TEMP, {nargs * 8}")
        self.asm_instructions.append("    sub TEMP, 32")  # 4*8 (RET + LCL + ARG + THIS)
        self.asm_instructions.append("    mov ARG, TEMP")

        # Reposition LCL
        self.asm_instructions.append("    mov LCL, SP")

        # Jump to function
        self.asm_instructions.append(f"    jmp {self.label(func_name)}")

        # Declare return label
        self.asm_instructions.append(f"{return_label}:")
        self.write_ln()

    def stubb_mem_alloc(self):
        self.asm_instructions.append("Memory_alloc:")
        self.write_ln()
        self.asm_instructions.append("    xor rax, rax")
        self.asm_instructions.append("    ret")

    def label(self, func_name):
        first, second = func_name.split(".")
        return (f"{first}_{second}")



