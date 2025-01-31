templates = {
'program' : '''declare i32 @printf(i8*, ...)

@linebreak_str = constant [2 x i8] c"\\0A\\00"
@integer_str   = constant [3 x i8] c"%d\\00"
@string_str   = constant [3 x i8] c"%s\\00"
@bool_str      = constant [11 x i8] c"false\\00true\\00"

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
'print_linebreak' : '''	call i32 (i8*, ...) @printf(ptr @linebreak_str)
''',
'print_string' : '''	call i32 (i8*, ...) @printf(ptr @string_str, ptr @{label})
''',
'print_bool' : '''{expr}
	%{label}.offset = select i1 %{label}, i32 6, i32 0
	%{label}.ptr = getelementptr [11 x i8], ptr @bool_str, i32 0, i32 %{label}.offset
	call i32 (i8*, ...) @printf(ptr %{label}.ptr)
''',
'print_int' : '''{expr}
	call i32 (i8*, ...)* @printf(ptr @integer_str, i32 %{label})
''',
}
