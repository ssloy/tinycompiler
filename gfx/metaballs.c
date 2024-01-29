#include <stdio.h>
#include <unistd.h>
#include <math.h>

#define FPS 24
#define WIDTH 80
#define HEIGHT 50
#define CLAMP(x, low, high) (((x) > (high)) ? (high) : (((x) < (low)) ? (low) : (x)))

float iTime = 0;

void mainImage(int fragCoord_x, int fragCoord_y) { // kinda shadertoy naming :)
    float u = (2.*fragCoord_x - WIDTH )/HEIGHT;
    float v = (2.*fragCoord_y - HEIGHT)/HEIGHT;
    float d1 = .6/sqrt(pow(sin(iTime*.5) -u, 2) + pow(sin(iTime*.5)-v, 2)); // linear motion
    float d2 = .6/sqrt(pow(sin(iTime*.5) -u, 2) + pow(cos(iTime*.5)-v, 2)); // circular motion
    float d3 = .6/sqrt(pow(sin(iTime*.25)-u, 2) + pow(sin(iTime)   -v, 2)); // wave
    float sdf = d1 + d2 + d3 - 2.2;          // metaballs signed distance function
    float fragColor_r = 255*1.7*(sdf+1);     // orange halo (red and green channels)
    float fragColor_g = 255*0.8*(sdf+1);
    float fragColor_b = 255*(sdf<0 ? 0 : 1); // cold-white metaballs (step function)
    printf("%d;%d;%d", CLAMP((int)fragColor_r,0,255), CLAMP((int)fragColor_g, 0, 255), CLAMP((int)fragColor_b, 0, 255));
}

int main() {
    printf("\033[2J\033[?25l"); // clear screen and hide cursor
    for (;;) {
        printf("\033[H"); // home
        for (int j = 0; j<HEIGHT; j+=2) {
            for (int i = 0; i<WIDTH; i++) {
                printf("\033[48;2;"); mainImage(i, j+0); printf("m");  // set background color
                printf("\033[38;2;"); mainImage(i, j+1); printf("m");  // set foreground color
                printf("\xE2\x96\x83");                                // half-block Unicode symbol
            }
            printf("\033[49m\n");
        }
        usleep(1000000/FPS);
        iTime += 1./FPS;
    }
    return 0;
}
