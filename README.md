# TinyCompiler - a 500-ish lines of code compiler in a weekend

Have you ever wondered how a compiler works, but you never found courage to find out?
Then this project is for you (**N.B.: a detailed description is available [here](https://ssloy.github.io/tinycompiler/)**).

I have never had the chance to look under the hood either, but one week-end I have decided to to write a translator from the esoteric programming language *wend* (short for week-end),
which I just invented myself, into regular GNU assembly.
The goal is to keep the code as tiny as possible, 500-ish lines of python sounds great.

Here is a program that uses virtually all concepts in Wend:
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
<img src="https://ssloy.github.io/tinycompiler/home/mandelbrot.png" width="336">

### Zero-player breakout game
![](https://ssloy.github.io/tinycompiler/home/breakout.gif)

### Fire
![](https://ssloy.github.io/tinycompiler/home/fire.gif)

### Sunset race
![](https://ssloy.github.io/tinycompiler/home/sunset-race.gif)

### Metaballs
![](https://ssloy.github.io/tinycompiler/home/metaballs.gif)



