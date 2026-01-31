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
        self.data_insert_pos = None
        self.VM_instructions = VM_instructions
        self.asm_instructions: List[str] = []
        self.label_count = 0
        self.string_id = 0
        self.string_literals = {}

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
        self.asm_instructions.append('fmt_str db "%s", 10, 0')
        self.asm_instructions.append('fmt_float db "%f", 10, 0')
        self.data_insert_pos = len(self.asm_instructions)
        self.write_ln()
        self.add_bss_section()
        self.add_text_section()
        self.runtime_setup()

    def add_bss_section(self):
        self.asm_instructions.append("section .bss")
        self.asm_instructions.append("vm_temp: resq 8")
        self.asm_instructions.append("vm_stack: resq 1024")
        self.asm_instructions.append("heap:     resb 65536")
        self.asm_instructions.append("heap_ptr: resq 1")
        self.write_ln()

    def add_text_section(self):
        self.asm_instructions.append("section .text")
        self.write_ln()

    def runtime_setup(self):
        self.stubb_mem_alloc()
        self.mem_alloc_bytes()
        self.asm_instructions.append("main:")
        self.asm_instructions.append("    push rbp")
        self.asm_instructions.append("    mov rbp, rsp")
        self.asm_instructions.append("    lea SP, [vm_stack]")  # Initialize VM stack pointer
        self.asm_instructions.append("    mov LCL, SP")  # lcl
        self.asm_instructions.append("    mov ARG, SP")  # arg
        self.asm_instructions.append("    xor THIS, THIS")  # this = 0
        self.asm_instructions.append("    lea rax, [heap]")
        self.asm_instructions.append("    mov [heap_ptr], rax")
        self.write_ln()
        self.call_vm_start()

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

            elif cmd == "add" :
                self.asm_instructions.append("    sub SP, 8  ; decrement stack pointer")
                self.asm_instructions.append("    mov rbx, [SP]  ; pop y")
                self.asm_instructions.append("    sub SP, 8  ; decrement stack pointer")
                self.asm_instructions.append("    mov rax, [SP]  ; pop x")
                self.asm_instructions.append("    add rax, rbx    ; x + y")
                self.push_rax()

            elif cmd == "faddf":
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

            elif cmd == "fsubf":
                self.asm_instructions.append("    sub SP, 8  ; decrement stack pointer")
                self.asm_instructions.append("    mov rax, [SP]  ; pop y")
                self.asm_instructions.append("    sub SP, 8  ; decrement stack pointer")
                self.asm_instructions.append("    mov rbx, [SP]  ; pop x")
                self.asm_instructions.append("    sub rbx, rax    ; x - y")
                self.push_rbx()


            elif cmd == "fadd":
                # y = int, x = float_fixed
                self.asm_instructions.append("    sub SP, 8")
                self.asm_instructions.append("    mov rbx, [SP]          ; y (int)")
                self.asm_instructions.append("    shl rbx, 16            ; y -> fixed")
                self.asm_instructions.append("    sub SP, 8")
                self.asm_instructions.append("    mov rax, [SP]          ; x (float_fixed)")
                self.asm_instructions.append("    add rax, rbx           ; x + y_fixed")
                self.push_rax()

            elif cmd == "fsub":
                # y = int, x = float_fixed
                self.asm_instructions.append("    sub SP, 8")
                self.asm_instructions.append("    mov rbx, [SP]          ; y (int)")
                self.asm_instructions.append("    shl rbx, 16            ; y -> fixed")
                self.asm_instructions.append("    sub SP, 8")
                self.asm_instructions.append("    mov rax, [SP]          ; x (float_fixed)")
                self.asm_instructions.append("    sub rax, rbx           ; x - y_fixed")
                self.push_rax()


            elif cmd == "addf":
                # y = float_fixed, x = int
                self.asm_instructions.append("    sub SP, 8")
                self.asm_instructions.append("    mov rbx, [SP]          ; y (float_fixed)")
                self.asm_instructions.append("    sub SP, 8")
                self.asm_instructions.append("    mov rax, [SP]          ; x (int)")
                self.asm_instructions.append("    shl rax, 16            ; x -> fixed")
                self.asm_instructions.append("    add rax, rbx           ; x_fixed + y")
                self.push_rax()

            elif cmd == "subf":
                self.asm_instructions.append("    sub SP, 8")
                self.asm_instructions.append("    mov rbx, [SP]          ; y (float_fixed)")
                self.asm_instructions.append("    sub SP, 8")
                self.asm_instructions.append("    mov rax, [SP]          ; x (int)")
                self.asm_instructions.append("    shl rax, 16            ; x -> fixed")
                self.asm_instructions.append("    sub rax, rbx           ; x_fixed - y")
                self.push_rax()



            elif cmd == "call":
                if len(parts) != 3:
                    raise ValueError(f"Invalid call instruction: {instr}")

                func_name = parts[1]
                nargs = int(parts[2])

                if func_name == "print.int" and nargs == 1:
                    self.write_print_int(parts)
                elif func_name == "print.float" and nargs == 1:
                    self.write_print_float()
                elif func_name == "print.String" and nargs == 1:
                    self.write_print_string()
                elif func_name == "Memory.alloc" and nargs == 1:
                    self.write_memory_alloc()
                elif func_name == "Math.multiply" and nargs == 2:
                    self.write_math_multiply_inline()
                elif func_name == "Math.fmultiplyf" and nargs == 2:
                    self.write_math_multiply_inline_float()
                elif func_name == "Math.fmultiply" and nargs == 2:
                    self.write_math_multiply_inline()
                elif func_name == "Math.multiplyf" and nargs == 2:
                    self.write_math_multiply_inline()
                elif func_name == "Math.divide" and nargs == 2:
                    self.write_math_divide_inline()
                elif func_name == "Math.fdivide" and nargs == 2:
                    self.write_math_divide_inline()
                elif func_name == "Math.dividef" and nargs == 2:
                    pass
                elif func_name == "Math.fdividef" and nargs == 2:
                    pass
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

            elif self.compare_arithmetic(cmd):
                self.write_cmp_arithmetic(cmd)

            elif cmd == "if-goto":
                if len(parts) != 2:
                    raise ValueError(f"Invalid if-goto instruction: {instr}")

                label = parts[1]
                self.pop_rax()
                self.asm_instructions.append("    cmp rax, 0")
                self.asm_instructions.append(f"    jne {label}")
                self.write_ln()

            elif cmd == "label":
                if len(parts) != 2:
                    raise ValueError(f"Invalid label instruction: {instr}")

                label = parts[1]
                self.asm_instructions.append(f"{label}:")
                self.write_ln()

            elif cmd == "goto":
                if len(parts) != 2:
                    raise ValueError(f"Invalid goto instruction: {instr}")

                label = parts[1]
                self.asm_instructions.append(f"    jmp {label}")
                self.write_ln()

    def write_fn_label(self, func_name, nlocals):
        if is_main_function(func_name):
            self.asm_instructions.append("vm_start:")
        else:
            class_name, func_name = func_name.split(".")
            print(func_name)
            self.asm_instructions.append(f"{class_name}_{func_name}:")
        self.create_stack_frame(nlocals)

    def push(self, parts):
        #if len(parts) != 3:
            #raise ValueError(f"Invalid push instruction: {' '.join(parts)}")

        segment = parts[1]
        index = parts[2]
        #print(segment, index)

        if segment == "constant":
            # if float do * 65536
            if '.' in index:
                float_value = float(index)
                int_value = int(float_value * 65536)
                #print(f"Converting float {float_value} to int {int_value} for push constant")
                self.push_constant(int_value)
            else:
                self.push_constant(index)
        elif segment == "local":
            self.push_local(index)
        elif segment == "argument":
            self.push_argument(index)
        elif segment == "this":
            self.push_this(index)
        elif segment == "pointer":
            self.push_pointer(index)
        elif segment == "string":
            self.push_string(parts[2:])
        elif segment == "temp":
            self.push_temp(index)
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

    def push_temp(self, index):
        self.asm_instructions.append(f"    mov rax, [rel vm_temp + {index}*8]")
        self.asm_instructions.append(f"    mov [SP], rax")
        self.asm_instructions.append(f"    add SP, 8  ; increment stack pointer")
        self.write_ln()

    def write_print_string(self):
        self.pop_rax()
        self.asm_instructions.append("    mov rsi, rax")
        self.asm_instructions.append("    lea rdi, [fmt_str]")
        self.asm_instructions.append("    xor eax, eax")
        self.asm_instructions.append("    sub rsp, 8")  # alignment (wichtig bei printf)
        self.asm_instructions.append("    call printf")
        self.asm_instructions.append("    add rsp, 8")
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
        elif segment == "pointer":
            self.pop_pointer(index)
        elif segment == "temp":
            self.pop_temp(index)

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

    def pop_temp(self, index):
        self.asm_instructions.append(f"    sub SP, 8  ; decrement stack pointer")
        self.asm_instructions.append(f"    mov rax, [SP]")
        self.asm_instructions.append(f"    mov [rel vm_temp + {int(index) * 8}], rax")
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
        self.asm_instructions.append("    mov r8, ARG")

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
        self.asm_instructions.append("    mov [r8 + rcx*8], rbx")
        self.asm_instructions.append(f"    jmp {loop_label}")

        self.asm_instructions.append(f"{done_label}:")

        # Set SP for caller: SP = (old ARG base) + count*8
        self.asm_instructions.append(f"    lea SP, [r8 + {count * 8}]")

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
        #self.asm_instructions.append("%define TEMP  r9")
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
        self.asm_instructions.append("    mov r8, SP")
        self.asm_instructions.append(f"    sub r8, {nargs * 8}")
        self.asm_instructions.append("    sub r8, 32")  # 4*8 (RET + LCL + ARG + THIS)
        self.asm_instructions.append("    mov ARG, r8")

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

    def call_vm_start(self):
        self.call_function("vm.start", 0)
        self.asm_instructions.append("    mov eax, 0")
        self.asm_instructions.append("    leave")
        self.asm_instructions.append("    ret")

    def compare_arithmetic(self, cmd):
        if cmd in ("eq", "gt", "lt"):
            return True

    def write_cmp_arithmetic(self, cmd):
        # pop y, pop x, cmp
        self.asm_instructions.append("    sub SP, 8  ; decrement stack pointer")
        self.asm_instructions.append("    mov rbx, [SP]  ; pop y")
        self.asm_instructions.append("    sub SP, 8  ; decrement stack pointer")
        self.asm_instructions.append("    mov rax, [SP]  ; pop x")
        self.asm_instructions.append("    cmp rax, rbx    ; compare x and y")

        # rax = 0/1 depending on cmd
        self.asm_instructions.append("    mov eax, 0       ; default result = 0")

        if cmd == "eq":
            self.asm_instructions.append("    sete al         ; al = 1 if x == y")
        elif cmd == "lt":
            self.asm_instructions.append("    setl al         ; al = 1 if x < y (signed)")
        elif cmd == "gt":
            self.asm_instructions.append("    setg al         ; al = 1 if x > y (signed)")
        else:
            raise ValueError(cmd)

        # push result
        self.asm_instructions.append("    mov [SP], rax   ; push result")
        self.asm_instructions.append("    add SP, 8       ; increment stack pointer")

    def push_string(self, param):

        raw = " ".join(param).strip()
        length, value = self.get_len(param)

        # Ensure literal exists in .data
        if raw not in self.string_literals:
            label = f"STR_LIT_{self.string_id}"
            self.string_id += 1
            self.string_literals[raw] = (label, length)

            # Minimal NASM escaping: double quotes
            value_escaped = value.replace('"', '""')

            lines = [
                f'{label}: db "{value_escaped}"',
                f'{label}_len equ {length}',
                ""
            ]

            for line in reversed(lines):
                self.asm_instructions.insert(self.data_insert_pos, line)
            self.data_insert_pos += len(lines)

        label, length = self.string_literals[raw]

        # allocate len+1 bytes on heap
        self.asm_instructions.append(f"    mov rdi, {length + 1}       ; bytes = len+1 for 0-terminator")
        self.asm_instructions.append("    call Memory_alloc_bytes      ; rax = dst pointer")
        self.asm_instructions.append("    mov rdx, rax                 ; save original dst pointer")

        # copy bytes from .data literal to heap
        self.asm_instructions.append(f"    lea rsi, [rel {label}]       ; source literal")
        self.asm_instructions.append("    mov rdi, rax                 ; destination in heap")
        self.asm_instructions.append(f"    mov rcx, {length}            ; number of bytes to copy")

        loop = f"STRCPY_LOOP{self.label_count}"
        done = f"STRCPY_DONE{self.label_count}"
        self.label_count += 1

        self.asm_instructions.append(f"{loop}:")
        self.asm_instructions.append("    test rcx, rcx")
        self.asm_instructions.append(f"    jz {done}")
        self.asm_instructions.append("    mov bl, [rsi]")
        self.asm_instructions.append("    mov [rdi], bl")
        self.asm_instructions.append("    inc rsi")
        self.asm_instructions.append("    inc rdi")
        self.asm_instructions.append("    dec rcx")
        self.asm_instructions.append(f"    jmp {loop}")
        self.asm_instructions.append(f"{done}:")

        # write 0 terminator
        self.asm_instructions.append("    mov byte [rdi], 0            ; terminator")

        # push pointer onto VM stack
        self.asm_instructions.append("    mov rax, rdx                 ; restore dst pointer for push")
        self.push_rax()



    def mem_alloc_bytes(self):
        self.asm_instructions.append("; Memory_alloc_bytes")
        self.asm_instructions.append("Memory_alloc_bytes:")
        self.asm_instructions.append("    ; rdi = num_bytes")
        self.asm_instructions.append("    mov rax, [heap_ptr]")
        self.asm_instructions.append("    lea rcx, [rax + rdi]")
        self.asm_instructions.append("    mov [heap_ptr], rcx")
        self.asm_instructions.append("    ret")



    def get_len(self, param):
        s = " ".join(param)
        str_value = s.strip('"')
        str_length = len(str_value)
        return str_length, str_value

    def write_memory_alloc(self):
        self.pop_rax()
        self.asm_instructions.append("    mov rdi, rax                 ; rdi = size")
        self.asm_instructions.append("    shl rdi , 3                  ; bytes = size * 8")
        self.asm_instructions.append("    call Memory_alloc_bytes      ; rax = dst pointer")
        self.write_ln()

        self.push_rax()

    def push_pointer(self, index):
        if index == "0":
            self.asm_instructions.append(f"    mov rax, THIS")
        elif index == "1":
            pass # dont have THAT segment implemented yet
        else:
            raise ValueError(f"Invalid pointer index: {index}")

        self.asm_instructions.append(f"    mov [SP], rax")
        self.asm_instructions.append(f"    add SP, 8  ; increment stack pointer")
        self.write_ln()

    def pop_pointer(self, index):
        self.asm_instructions.append(f"    sub SP, 8  ; decrement stack pointer")
        self.asm_instructions.append(f"    mov rax, [SP]")

        if index == "0":
            self.asm_instructions.append(f"    mov THIS, rax")
        elif index == "1":
            pass # dont have THAT segment implemented yet

    def write_print_float(self):
        self.pop_rax()
        self.asm_instructions.append("    cvtsi2sd xmm0, rax        ; convert int to double")
        self.asm_instructions.append("    mov rbx, 65536")
        self.asm_instructions.append("    cvtsi2sd xmm1, rbx        ; convert int to double (65536)")
        self.asm_instructions.append("    divsd xmm0, xmm1          ; divide by 65536 to get float")

        self.asm_instructions.append("    lea rdi, [fmt_float]")
        self.asm_instructions.append("    mov eax, 1")
        #self.asm_instructions.append("    sub rsp, 8                 ; align stack for printf")
        self.asm_instructions.append("    call printf")
        #self.asm_instructions.append("    add rsp, 8")

    def write_math_multiply_inline(self):
        # pop y
        self.asm_instructions.append("    sub SP, 8")
        self.asm_instructions.append("    mov rbx, [SP]          ; y")
        # pop x
        self.asm_instructions.append("    sub SP, 8")
        self.asm_instructions.append("    mov rax, [SP]          ; x")
        # rax = x * y
        self.asm_instructions.append("    imul rax, rbx          ; x*y")
        # push result
        self.push_rax()

    def write_math_multiply_inline_float(self):
        # pop y
        self.asm_instructions.append("    sub SP, 8")
        self.asm_instructions.append("    mov rbx, [SP]          ; y")
        # pop x
        self.asm_instructions.append("    sub SP, 8")
        self.asm_instructions.append("    mov rax, [SP]          ; x")
        # rax = x * y
        self.asm_instructions.append("    imul rbx               ; x*y in rdx:rax")
        self.asm_instructions.append("    shr rax, 16            ; adjust fixed-point (divide by 65536)")
        # push result
        self.push_rax()

    def write_math_divide_inline(self):
        # pop y
        self.asm_instructions.append("    sub SP, 8")
        self.asm_instructions.append("    mov rbx, [SP]          ; y")
        # pop x
        self.asm_instructions.append("    sub SP, 8")
        self.asm_instructions.append("    mov rax, [SP]          ; x")
        # rax = x / y
        self.asm_instructions.append("    cqo                     ; sign-extend rax to rdx:rax")
        self.asm_instructions.append("    idiv rbx                ; rax = x / y")
        # push result
        self.push_rax()






