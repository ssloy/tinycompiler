> # N.B.: Under construction: I am happy with the code, but I need some time to write a series of articles explaining the things under the hood. It is highly likely that I'll extend the code to make the compiler optimising
> current description draft (in russian) is available here: https://habr.com/ru/articles/786158/

> in fact, [tinyoptimizer](https://github.com/ssloy/tinyoptimizer) is actually happening (work in progress) :)

# tinycompiler - a 500-ish lines of code compiler in a weekend
Have you ever wondered how a compiler works? If so, this project is for you.

This weekend I'll write a compiler that translates a code written in a very simple programming language Wend (short for a week-end) into GNU assembly.
This repository, however, will contain more than the final code. It will tell you a story about compilers.

So behold, here is a program that uses virtually all concepts in Wend:
```cpp
main() {
    // square root of a fixed-point number
    // stored in a 32 bit integer variable, shift is the precision

    int sqrt(int n, int shift) {
        int x;
        int x_old;
        int n_one;

        if n > 2147483647/shift { // pay attention to potential overflows
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

    int abs(int x) {
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

## run tests
```sh
make test
```

## Graphics!
It is so dull to compute Fibonacci numbers, so here are more eyecandy examples for our compiler,  check test-programs/gfx/*.wend files.
```sh
make gfx
```
### Mandelbrot set
<img src="https://raw.githubusercontent.com/ssloy/ssloy.github.io/main/docs/tinycompiler/gfx/mandelbrot.png" width="336">

### Zero-player breakout game
![](https://raw.githubusercontent.com/ssloy/ssloy.github.io/main/docs/tinycompiler/gfx/breakout.gif)

### Fire
![](https://raw.githubusercontent.com/ssloy/ssloy.github.io/main/docs/tinycompiler/gfx/fire6.gif)

### Sunset race
![](https://raw.githubusercontent.com/ssloy/ssloy.github.io/main/docs/tinycompiler/gfx/sunset-race.gif)

### Metaballs
![](https://raw.githubusercontent.com/ssloy/ssloy.github.io/main/docs/tinycompiler/gfx/metaballs.gif)



