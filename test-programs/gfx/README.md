# Graphics!
It is so dull to compute Fibonacci numbers, so here are more eyecandy examples for tinycompiler.

### build wend version:
```sh
git clone https://github.com/ssloy/tinycompiler.git &&
cd tinycompiler &&
make gfx
```

### build C version:
```sh
git clone https://github.com/ssloy/tinycompiler.git &&
cd tinycompiler/test-programs/gfx/ &&
gcc breakout.c -o breakout &&
gcc fire.c -o fire &&
gcc mandelbrot.c -o mandelbrot &&
gcc metaballs.c -o metaballs -lm &&
gcc race.c -o race -lm
```

### Mandelbrot set
<img src="https://ssloy.github.io/tinycompiler/home/mandelbrot.png" width="336">

### Ray tracer
![](https://ssloy.github.io/tinycompiler/home/raytracer.png)

### Zero-player breakout game
![](https://ssloy.github.io/tinycompiler/home/breakout.gif)

### Fire
![](https://ssloy.github.io/tinycompiler/home/fire.gif)

### Sunset race
![](https://ssloy.github.io/tinycompiler/home/sunset-race.gif)

### Metaballs
![](https://ssloy.github.io/tinycompiler/home/metaballs.gif)
