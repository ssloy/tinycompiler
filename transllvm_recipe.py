templates = {
'program' : '''declare i32 @printf(i8*, ...)

@newline = constant [ 2 x i8] c"\\0A\\00"
@integer = constant [ 3 x i8] c"%d\\00"
@string  = constant [ 3 x i8] c"%s\\00"
@bool    = constant [11 x i8] c"false\\00true\\00"

{strings}
define i32 @main() {{
	call void @{main}()
	ret i32 0
}}
{functions}
''',
'alloca1' : '''	%{name} = alloca {vartype}
	store {vartype} %{name}.arg, {vartype}* %{name}
''',
'alloca2' : '''	%{name} = alloca {vartype}
''',
'function' : '''define {rettype} @{label}({args}) {{
{alloca1}
{alloca2}
{body}
	{retval}
}}
{nested}
''',
'ascii' : '''@{label} = constant [{size} x i8] c"{string}\\00"
''',
'print_newline' : '''	call i32 (i8*, ...) @printf(ptr @newline)
''',
'print_string' : '''	call i32 (i8*, ...) @printf(ptr @string, ptr @{label})
''',
'print_bool' : '''{expr}
	%{label}.offset = select i1 %{label}, i32 6, i32 0
	%{label}.ptr = getelementptr [11 x i8], ptr @bool, i32 0, i32 %{label}.offset
	call i32 (i8*, ...) @printf(ptr %{label}.ptr)
''',
'print_int' : '''{expr}	call i32 (i8*, ...)* @printf(ptr @integer, i32 %{label})
''',
'assign' : '''{expr}	store {vartype} %{label}, {vartype}* %{varname}
''',
'while' : '''	br label %{label2}.cond
{label2}.cond:
{expr}
	br i1 %{label1}, label %{label2}.body, label %{label2}.end
{label2}.body:
{body}
	br label %{label2}.cond
{label2}.end:
''',
'ifthenelse' : '''{expr}	br i1 %{label1}, label %{label2}.then, label %{label2}.else
{label2}.then:
{ibody}	br label %{label2}.end
{label2}.else:
{ebody}	br label %{label2}.end
{label2}.end:
''',
'return' : '''{expr}	ret {rettype} %{label}
'''
}
