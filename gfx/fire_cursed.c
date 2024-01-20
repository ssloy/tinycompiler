#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <unistd.h>

#define WIDTH 80
#define HEIGHT 25
#define FPS 30

const char* palette[256] = {
#define ANSIRGB(R,G,B) "\033[48;2;" #R ";"  #G ";" #B "m "
    ANSIRGB(  0,  0,   0), ANSIRGB(  0,   4,  4), ANSIRGB(  0,  16, 20), ANSIRGB(  0,  28,  36),
    ANSIRGB(  0,  32, 44), ANSIRGB(  0,  36, 48), ANSIRGB( 60,  24, 32), ANSIRGB(100,  16,  16),
    ANSIRGB(132,  12, 12), ANSIRGB(160,   8,  8), ANSIRGB(192,   8,  8), ANSIRGB(220,   4,   4),
    ANSIRGB(252,   0,  0), ANSIRGB(252,   0,  0), ANSIRGB(252,  12,  0), ANSIRGB(252,  28,   0),
    ANSIRGB(252,  40,  0), ANSIRGB(252,  52,  0), ANSIRGB(252,  64,  0), ANSIRGB(252,  80,   0),
    ANSIRGB(252,  92,  0), ANSIRGB(252, 104,  0), ANSIRGB(252, 116,  0), ANSIRGB(252, 132,   0),
    ANSIRGB(252, 144,  0), ANSIRGB(252, 156,  0), ANSIRGB(252, 156,  0), ANSIRGB(252, 160,   0),
    ANSIRGB(252, 160,  0), ANSIRGB(252, 164,  0), ANSIRGB(252, 168,  0), ANSIRGB(252, 168,   0),
    ANSIRGB(252, 172,  0), ANSIRGB(252, 176,  0), ANSIRGB(252, 176,  0), ANSIRGB(252, 180,   0),
    ANSIRGB(252, 180,  0), ANSIRGB(252, 184,  0), ANSIRGB(252, 188,  0), ANSIRGB(252, 188,   0),
    ANSIRGB(252, 192,  0), ANSIRGB(252, 196,  0), ANSIRGB(252, 196,  0), ANSIRGB(252, 200,   0),
    ANSIRGB(252, 204,  0), ANSIRGB(252, 204,  0), ANSIRGB(252, 208,  0), ANSIRGB(252, 212,   0),
    ANSIRGB(252, 212,  0), ANSIRGB(252, 216,  0), ANSIRGB(252, 220,  0), ANSIRGB(252, 220,   0),
    ANSIRGB(252, 224,  0), ANSIRGB(252, 228,  0), ANSIRGB(252, 228,  0), ANSIRGB(252, 232,   0),
    ANSIRGB(252, 232,  0), ANSIRGB(252, 236,  0), ANSIRGB(252, 240,  0), ANSIRGB(252, 240,   0),
    ANSIRGB(252, 244,  0), ANSIRGB(252, 248,  0), ANSIRGB(252, 248,  0), ANSIRGB(252, 252,   0),
#define W ANSIRGB(252,252,252)
    W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W,
    W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W,
    W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W,
    W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W,
    W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W,
    W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W,
    W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W,
    W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W, W
#undef W
#undef ANSIRGB
};

#define EVAL(...)  EVAL1(EVAL1(EVAL1(__VA_ARGS__)))
#define EVAL1(...) EVAL2(EVAL2(EVAL2(__VA_ARGS__)))
#define EVAL2(...) EVAL3(EVAL3(EVAL3(__VA_ARGS__)))
#define EVAL3(...) EVAL4(EVAL4(EVAL4(__VA_ARGS__)))
#define EVAL4(...) EVAL5(EVAL5(EVAL5(__VA_ARGS__)))
#define EVAL5(...) __VA_ARGS__

#define CONCAT(a,b) a##b

#define IF_ELSE(b) CONCAT(IF_,b)
#define IF_0(...) ELSE_0
#define IF_1(...) __VA_ARGS__ ELSE_1
#define ELSE_0(...) __VA_ARGS__
#define ELSE_1(...)

#define SECOND(a, b, ...) b
#define TEST(...) SECOND(__VA_ARGS__, 0)
#define ISZERO(n) TEST(ISZERO_ ## n)
#define ISZERO_0 ~, 1

#define DEC(n) CONCAT(DEC_, n)
#define DEC_0 0
#define DEC_1 0
#define DEC_2 1
#define DEC_3 2
#define DEC_4 3
#define DEC_5 4
#define DEC_6 5
#define DEC_7 6
#define DEC_8 7
#define DEC_9 8
#define DEC_10 9
#define DEC_11 10

#define EMPTY()
#define DELAY(id) id EMPTY()
#define DELAY2(...) __VA_ARGS__ DELAY(EMPTY)()

#define DEPTH 11
#define FIRE(d,id) \
    IF_ELSE(ISZERO(d)) \
    ( uint8_t id; ) \
    ( \
        DELAY2(FIRE_)( DEC(d), id##0 ) \
        DELAY2(FIRE_)( DEC(d), id##1 ) \
    )
#define FIRE_(...) DELAY(FIRE)(__VA_ARGS__)
EVAL(FIRE(DEPTH,fire))

uint8_t get_fire(int i) {
#define GETTER(d,m,id) \
    IF_ELSE(ISZERO(d)) \
    ( return id; ) \
    ( \
      if (i<(m)) \
        DELAY2(GETTER_)(DEC(d), ((m)-(1<<DEC(DEC(d)))), id##0) \
      else \
        DELAY2(GETTER_)(DEC(d), ((m)+(1<<DEC(DEC(d)))), id##1) \
    )
#define GETTER_(...) DELAY(GETTER) (__VA_ARGS__)
    EVAL(GETTER(DEPTH,1<<(DEPTH-1),fire));
}

void set_fire(int i, uint8_t v) {
#define SETTER(d,m,id) \
    IF_ELSE(ISZERO(d)) \
    ( id = v; ) \
    ( \
      if (i<(m)) \
        DELAY2(SETTER_)(DEC(d), ((m)-(1<<DEC(DEC(d)))), id##0) \
      else \
        DELAY2(SETTER_)(DEC(d), ((m)+(1<<DEC(DEC(d)))), id##1) \
    )
#define SETTER_(...) DELAY(SETTER)(__VA_ARGS__)
    EVAL(SETTER(DEPTH,1<<(DEPTH-1),fire));
}

void line_blur(int offset, int step, int nsteps) {
    uint8_t circ[3] = {0, get_fire(offset), get_fire(offset+step)};
    uint8_t beg = 1;
    for (int i=0; i<nsteps; i++) {
        set_fire(offset, (circ[0]+circ[1]+circ[2])/3);
        circ[(beg+++2)%3] = i+2<nsteps ? get_fire(offset+2*step) : 0;
        offset += step;
    }
}

int main() {
    printf("\033[2J"); // clear screen
    for (;;) {
        printf("\033[H"); // home

        for (int j = 1; j<HEIGHT; j++)        // scroll up
            for (int i = 0; i<WIDTH; i++)
                set_fire(i+(j-1)*WIDTH, get_fire(i+j*WIDTH));

        // box blur: first horizontal motion blur then vertical motion blur
        for (int j = 0; j<HEIGHT; j++)
            line_blur(j*WIDTH, 1, WIDTH);
        for (int i = 0; i<WIDTH; i++)
            line_blur(i, WIDTH, HEIGHT);

        for (int i = 0; i< WIDTH*HEIGHT; i++) // cool
            if (rand()%2 && get_fire(i)>0)
                set_fire(i, get_fire(i)-1);

        for (int i = 0; i<WIDTH; i++) {       // add heat to the bed
            int idx = i+(HEIGHT-1)*WIDTH;
            if (!(rand()%32))
                set_fire(idx, 128+rand()%128);   // sparks
            else
                set_fire(idx, get_fire(idx)<16 ? 16 : get_fire(idx)); // ember bed
        }

        for (int j = 0; j<HEIGHT; j++) {      // show the buffer
            for (int i = 0; i<WIDTH; i++)
                printf(palette[get_fire(i+j*WIDTH)]);
            printf("\033[49m\n");
        }
        usleep(1000000/FPS);
    }
    return 0;
}

