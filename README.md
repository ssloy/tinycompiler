# tinycompiler - a 500-ish lines of code compiler in a weekend
Have you ever wondered how a compiler works? If so, this project is for you.

This weekend I'll write a compiler that translates a code written in a very simple programming language Wend (short for a week-end) into GNU assembly.
This repository, however, will contain more than the final code. It will tell you a story about compilers.

So behold, here is a program that uses virtually all concepts in Wend:
```cpp
fun main() {
    // square root of a fixed-point number
    // stored in a 32 bit integer variable, shift is the precision

    fun sqrt(n:int, shift:int) : int {
        var x:int;
        var x_old:int;
        var n_one:int;

        if n > 65535 { // pay attention to potential overflows
            return 2 * sqrt(n / 4, shift);
        }
        x = shift; // initial guess 1.0, can do better, but oh well
        n_one = n * shift; // need to compensate for fixp division
        while true {
            x_old = x;
            x = (x + n_one / x) / 2;
            if abs(x - x_old) <= 1 {
                return x;
            }
        }
    }

    fun abs(x:int) : int {
        if x < 0 {
            return -x;
        } else {
            return x;
        }
    }

    // 25735 is approximately equal to pi * 8192;
    // expected value of the output is sqrt(pi) * 8192 approx 14519

    println sqrt(25735, 8192);
}
```

There will no be dynamic memory allocation, no pointers, no garbage collection. There will be nested functions, function overloading and type checking.

And as usual, there will be a program with a raytracer :)
