default rel
; Aliases
%define SP    r12
%define LCL   r13
%define ARG   r14
%define THIS  r15
%define FRAME r10
%define RET   r11


global main
global Memory_alloc
extern printf

section .data
fmt_int db "%d", 10, 0
fmt_str db "%s", 10, 0
fmt_float db "%f", 10, 0
STR_LIT_0: db "=== Counter Demo ==="
STR_LIT_0_len equ 20

STR_LIT_1: db "i:"
STR_LIT_1_len equ 2

STR_LIT_2: db "Reached 3"
STR_LIT_2_len equ 9

STR_LIT_3: db "Sum:"
STR_LIT_3_len equ 4


section .bss
vm_temp: resq 8
vm_stack: resq 1024
heap:     resb 65536
heap_ptr: resq 1

section .text

Memory_alloc:

    xor rax, rax
    ret
; Memory_alloc_bytes
Memory_alloc_bytes:
    ; rdi = num_bytes
    mov rax, [heap_ptr]
    lea rcx, [rax + rdi]
    mov [heap_ptr], rcx
    ret
DIV_BY_ZERO:
    lea rdi, [rel div_by_zero_msg]
    xor eax, eax
    call printf
    mov eax, 1
    leave
    ret

div_by_zero_msg db "Error: Division by zero", 10, 0

main:
    push rbp
    mov rbp, rsp
    lea SP, [vm_stack]
    mov LCL, SP
    mov ARG, SP
    xor THIS, THIS
    lea rax, [heap]
    mov [heap_ptr], rax

    lea RET, [rel RET_LABEL0]
    mov [SP], RET
    add SP, 8  ; increment stack pointer
    mov [SP], LCL
    add SP, 8  ; increment stack pointer
    mov [SP], ARG
    add SP, 8  ; increment stack pointer
    mov [SP], THIS
    add SP, 8  ; increment stack pointer
    mov r8, SP
    sub r8, 0
    sub r8, 32
    mov ARG, r8
    mov LCL, SP
    jmp vm_start
RET_LABEL0:

    mov eax, 0
    leave
    ret
Test_new:

    mov rax, 0
    mov [SP], rax
    add SP, 8  ; increment stack pointer

    sub SP, 8  ; decrement stack pointer
    mov rax , [SP]  ; pop value into rax
    mov rdi, rax                 ; rdi = size
    shl rdi , 3                  ; bytes = size * 8
    call Memory_alloc_bytes      ; rax = dst pointer

    mov [SP], rax
    add SP, 8  ; increment stack pointer

    sub SP, 8  ; decrement stack pointer
    mov rax, [SP]
    mov THIS, rax
    mov rax, THIS
    mov [SP], rax
    add SP, 8  ; increment stack pointer

    mov FRAME, LCL
    mov RET, [FRAME - 32]
    lea rax, [SP - 8]
    mov r8, ARG
    mov THIS, [FRAME - 8]
    mov ARG,  [FRAME - 16]
    mov LCL,  [FRAME - 24]
    mov rcx, 1
RET_COPY_LOOP1:
    test rcx, rcx
    jz RET_COPY_DONE1
    dec rcx
    mov rbx, [rax + rcx*8]
    mov [r8 + rcx*8], rbx
    jmp RET_COPY_LOOP1
RET_COPY_DONE1:
    lea SP, [r8 + 8]
    jmp RET

vm_start:
    mov qword [SP], 0
    add SP, 8  ; increment stack pointer
    mov qword [SP], 0
    add SP, 8  ; increment stack pointer

    mov rdi, 21       ; bytes = len+1 for 0-terminator
    call Memory_alloc_bytes      ; rax = dst pointer
    mov rdx, rax                 ; save original dst pointer
    lea rsi, [rel STR_LIT_0]       ; source literal
    mov rdi, rax                 ; destination in heap
    mov rcx, 20            ; number of bytes to copy
STRCPY_LOOP2:
    test rcx, rcx
    jz STRCPY_DONE2
    mov bl, [rsi]
    mov [rdi], bl
    inc rsi
    inc rdi
    dec rcx
    jmp STRCPY_LOOP2
STRCPY_DONE2:
    mov byte [rdi], 0            ; terminator
    mov rax, rdx                 ; restore dst pointer for push
    mov [SP], rax
    add SP, 8  ; increment stack pointer

    sub SP, 8  ; decrement stack pointer
    mov rax , [SP]  ; pop value into rax
    mov rsi, rax
    lea rdi, [fmt_str]
    xor eax, eax
    sub rsp, 8
    call printf
    add rsp, 8

    mov rax, 0
    mov [SP], rax
    add SP, 8  ; increment stack pointer

    sub SP, 8  ; decrement stack pointer
    mov rax, [SP]
    mov [LCL + 0], rax

    mov rax, 0
    mov [SP], rax
    add SP, 8  ; increment stack pointer

    sub SP, 8  ; decrement stack pointer
    mov rax, [SP]
    mov [LCL + 8], rax

LOOP_START0:

    mov rax, [LCL + 8]
    mov [SP], rax
    add SP, 8  ; increment stack pointer

    mov rax, 5
    mov [SP], rax
    add SP, 8  ; increment stack pointer

    sub SP, 8  ; decrement stack pointer
    mov rbx, [SP]  ; pop y
    sub SP, 8  ; decrement stack pointer
    mov rax, [SP]  ; pop x
    cmp rax, rbx    ; compare x and y
    mov eax, 0       ; default result = 0
    setl al         ; al = 1 if x < y (signed)
    mov [SP], rax   ; push result
    add SP, 8       ; increment stack pointer
    sub SP, 8  ; decrement stack pointer
    mov rax , [SP]  ; pop value into rax
    cmp rax, 0
    jne LOOP_BODY0

    jmp LOOP_END0

LOOP_BODY0:

    mov rdi, 3       ; bytes = len+1 for 0-terminator
    call Memory_alloc_bytes      ; rax = dst pointer
    mov rdx, rax                 ; save original dst pointer
    lea rsi, [rel STR_LIT_1]       ; source literal
    mov rdi, rax                 ; destination in heap
    mov rcx, 2            ; number of bytes to copy
STRCPY_LOOP3:
    test rcx, rcx
    jz STRCPY_DONE3
    mov bl, [rsi]
    mov [rdi], bl
    inc rsi
    inc rdi
    dec rcx
    jmp STRCPY_LOOP3
STRCPY_DONE3:
    mov byte [rdi], 0            ; terminator
    mov rax, rdx                 ; restore dst pointer for push
    mov [SP], rax
    add SP, 8  ; increment stack pointer

    sub SP, 8  ; decrement stack pointer
    mov rax , [SP]  ; pop value into rax
    mov rsi, rax
    lea rdi, [fmt_str]
    xor eax, eax
    sub rsp, 8
    call printf
    add rsp, 8

    mov rax, [LCL + 8]
    mov [SP], rax
    add SP, 8  ; increment stack pointer

    sub SP, 8  ; decrement stack pointer
    mov rax , [SP]  ; pop value into rax
    mov rsi, rax
    lea rdi, [fmt_int]
    xor rax, rax
    call printf
    mov rax, [LCL + 0]
    mov [SP], rax
    add SP, 8  ; increment stack pointer

    mov rax, [LCL + 8]
    mov [SP], rax
    add SP, 8  ; increment stack pointer

    sub SP, 8  ; decrement stack pointer
    mov rbx, [SP]  ; pop y
    sub SP, 8  ; decrement stack pointer
    mov rax, [SP]  ; pop x
    add rax, rbx    ; x + y
    mov [SP], rax
    add SP, 8  ; increment stack pointer

    sub SP, 8  ; decrement stack pointer
    mov rax, [SP]
    mov [LCL + 0], rax

    mov rax, [LCL + 8]
    mov [SP], rax
    add SP, 8  ; increment stack pointer

    mov rax, 3
    mov [SP], rax
    add SP, 8  ; increment stack pointer

    sub SP, 8  ; decrement stack pointer
    mov rbx, [SP]  ; pop y
    sub SP, 8  ; decrement stack pointer
    mov rax, [SP]  ; pop x
    cmp rax, rbx    ; compare x and y
    mov eax, 0       ; default result = 0
    sete al         ; al = 1 if x == y
    mov [SP], rax   ; push result
    add SP, 8       ; increment stack pointer
    sub SP, 8  ; decrement stack pointer
    mov rax , [SP]  ; pop value into rax
    cmp rax, 0
    jne IF_TRUE1

    jmp IF_FALSE1

IF_TRUE1:

    mov rdi, 10       ; bytes = len+1 for 0-terminator
    call Memory_alloc_bytes      ; rax = dst pointer
    mov rdx, rax                 ; save original dst pointer
    lea rsi, [rel STR_LIT_2]       ; source literal
    mov rdi, rax                 ; destination in heap
    mov rcx, 9            ; number of bytes to copy
STRCPY_LOOP4:
    test rcx, rcx
    jz STRCPY_DONE4
    mov bl, [rsi]
    mov [rdi], bl
    inc rsi
    inc rdi
    dec rcx
    jmp STRCPY_LOOP4
STRCPY_DONE4:
    mov byte [rdi], 0            ; terminator
    mov rax, rdx                 ; restore dst pointer for push
    mov [SP], rax
    add SP, 8  ; increment stack pointer

    sub SP, 8  ; decrement stack pointer
    mov rax , [SP]  ; pop value into rax
    mov rsi, rax
    lea rdi, [fmt_str]
    xor eax, eax
    sub rsp, 8
    call printf
    add rsp, 8

IF_FALSE1:

    mov rax, [LCL + 8]
    mov [SP], rax
    add SP, 8  ; increment stack pointer

    mov rax, 1
    mov [SP], rax
    add SP, 8  ; increment stack pointer

    sub SP, 8  ; decrement stack pointer
    mov rbx, [SP]  ; pop y
    sub SP, 8  ; decrement stack pointer
    mov rax, [SP]  ; pop x
    add rax, rbx    ; x + y
    mov [SP], rax
    add SP, 8  ; increment stack pointer

    sub SP, 8  ; decrement stack pointer
    mov rax, [SP]
    mov [LCL + 8], rax

    jmp LOOP_START0

LOOP_END0:

    mov rdi, 5       ; bytes = len+1 for 0-terminator
    call Memory_alloc_bytes      ; rax = dst pointer
    mov rdx, rax                 ; save original dst pointer
    lea rsi, [rel STR_LIT_3]       ; source literal
    mov rdi, rax                 ; destination in heap
    mov rcx, 4            ; number of bytes to copy
STRCPY_LOOP5:
    test rcx, rcx
    jz STRCPY_DONE5
    mov bl, [rsi]
    mov [rdi], bl
    inc rsi
    inc rdi
    dec rcx
    jmp STRCPY_LOOP5
STRCPY_DONE5:
    mov byte [rdi], 0            ; terminator
    mov rax, rdx                 ; restore dst pointer for push
    mov [SP], rax
    add SP, 8  ; increment stack pointer

    sub SP, 8  ; decrement stack pointer
    mov rax , [SP]  ; pop value into rax
    mov rsi, rax
    lea rdi, [fmt_str]
    xor eax, eax
    sub rsp, 8
    call printf
    add rsp, 8

    mov rax, [LCL + 0]
    mov [SP], rax
    add SP, 8  ; increment stack pointer

    sub SP, 8  ; decrement stack pointer
    mov rax , [SP]  ; pop value into rax
    mov rsi, rax
    lea rdi, [fmt_int]
    xor rax, rax
    call printf
    mov rax, 0
    mov [SP], rax
    add SP, 8  ; increment stack pointer

    mov FRAME, LCL
    mov RET, [FRAME - 32]
    lea rax, [SP - 0]
    mov r8, ARG
    mov THIS, [FRAME - 8]
    mov ARG,  [FRAME - 16]
    mov LCL,  [FRAME - 24]
    mov rcx, 0
RET_COPY_LOOP6:
    test rcx, rcx
    jz RET_COPY_DONE6
    dec rcx
    mov rbx, [rax + rcx*8]
    mov [r8 + rcx*8], rbx
    jmp RET_COPY_LOOP6
RET_COPY_DONE6:
    lea SP, [r8 + 0]
    jmp RET

    mov eax, 0
    leave
    ret