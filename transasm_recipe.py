templates = {
'ascii' : '''{label}: .ascii "{string}"
	{label}_len = . - {label}
''',

'var' : '''	movl display+{scope}, %eax
	movl -{variable}(%eax), %eax
''',

'print_linebreak' : '''	pushl $10           # '\\n'
	movl $4, %eax       # write system call
	movl $1, %ebx       # stdout
	leal 0(%esp), %ecx  # address of the character
	movl $1, %edx       # one byte
	int  $0x80          # make system call
	addl $4, %esp
''',

'print_int' : '''{expr}
	pushl %eax
	call print_int32
	addl $4, %esp
{newline}
''',

'print_string' : '''	movl $4, %eax
	movl $1, %ebx
	movl ${label}, %ecx
	movl ${label}_len, %edx
	int  $0x80
{newline}
''',

'print_bool' : '''{expr}
	movl $truestr, %ecx
	movl $truestr_len, %edx
	test %eax, %eax
	jnz 0f
	movl $falsestr, %ecx
	movl $falsestr_len, %edx
0:	movl $4, %eax
	movl $1, %ebx
	int  $0x80
{newline}
''',

'assign' : '''{expression}
	pushl %eax
	movl display+{scope}, %eax
	popl %ebx
	movl %ebx, -{variable}(%eax)
''',

'ifthenelse' : '''{condition}
	test %eax, %eax
	jz {label1}
{ibody}
	jmp {label2}
{label1}:
{ebody}
{label2}:
''',

'while' : '''{label1}:
{condition}
	test %eax, %eax
	jz {label2}
{body}
	jmp {label1}
{label2}:
''',

'funcall' : '''	pushl display+{scope}
{allocargs}
	subl ${varsize}, %esp
	leal {disphead}(%esp), %eax
	movl %eax, display+{scope}
	call {funlabel}
	movl display+{scope}, %esp
	addl $4, %esp
	popl display+{scope}
''',

'program' : '''.global _start
	.data
{strings}
truestr: .ascii "true"
	truestr_len = . - truestr
falsestr: .ascii "false"
	falsestr_len = . - falsestr
	.align 2
display: .skip {display_size}
	.text
_start:
	leal -4(%esp), %eax
	movl %eax, display+{offset}
	subl ${varsize}, %esp # allocate locals
	call {main}
	addl ${varsize}, %esp # deallocate locals
_end:               # do not care about clearing the stack
	movl $1, %eax   # _exit system call (check asm/unistd_32.h for the table)
	movl $0, %ebx   # error code 0
	int $0x80       # make system call
{functions}
print_int32:
	movl 4(%esp), %eax  # the number to print
	cdq
	xorl %edx, %eax
	subl %edx, %eax     # abs(%eax)
	pushl $10           # base 10
	movl %esp, %ecx     # buffer for the string to print
	subl $16, %esp      # max 10 digits for a 32-bit number (keep %esp dword-aligned)
0:	xorl %edx, %edx     #     %edx = 0
	divl 16(%esp)       #     %eax = %edx:%eax/10 ; %edx = %edx:%eax % 10
	decl %ecx           #     allocate one more digit
	addb $48, %dl       #     %edx += '0'       # 0,0,0,0,0,0,0,0,0,0,'1','2','3','4','5','6'
	movb %dl, (%ecx)    #     store the digit   # ^                   ^                    ^
	test %eax, %eax     #                       # %esp                %ecx (after)         %ecx (before)
	jnz 0b              # until %eax==0         #                     <----- %edx = 6 ----->
	cmp %eax, 24(%esp)  # if the number is negative
	jge 0f
	decl %ecx           # allocate one more character
	movb $45, 0(%ecx)   # '-'
0:	movl $4, %eax       # write system call
	movl $1, %ebx       # stdout
	leal 16(%esp), %edx # the buffer to print
	subl %ecx, %edx     # number of digits
	int $0x80           # make system call
	addl $20, %esp      # deallocate the buffer
	ret
'''
}
