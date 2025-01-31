templates = {
'program' : '''declare i32 @printf(i8*, ...)

@newline = constant [ 2 x i8] c"\\0A\\00"
@integer = constant [ 3 x i8] c"%d\\00"
@string  = constant [ 3 x i8] c"%s\\00"
@bool    = constant [11 x i8] c"false\\00true\\00"

{strings}
define void @main() {{
	call void @{main}()
	ret void
}}
{functions}
''',
'function' : '''define {rettype} @{label}() {{
{body}
	{retval}
}}
''',
'ascii' : '''@{label} = constant [{size} x i8] c"{string}\\00"
''',
'print_newline' : '''	call i32 (i8*, ...) @printf(ptr @newline)
''',
'printing' : '''	call i32 (i8*, ...) @printf(ptr @string, ptr @{label})
''',
'print_bool' : '''{expr}
	%{label}.offset = select i1 %{label}, i32 6, i32 0
	%{label}.ptr = getelementptr [11 x i8], ptr @bool, i32 0, i32 %{label}.offset
	call i32 (i8*, ...) @printf(ptr %{label}.ptr)
''',
'print_int' : '''{expr}
	call i32 (i8*, ...)* @printf(ptr @integer, i32 %{label})
''',
}
