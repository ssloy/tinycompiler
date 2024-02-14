#include <stdio.h>
#include <unistd.h>
#include <math.h>

#define FPS 24
#define MULTI 2
#define WIDTH (80*MULTI)
#define HEIGHT (50*MULTI)
#define CLAMP(x, low, high) (((x) > (high)) ? (high) : (((x) < (low)) ? (low) : (x)))
float iTime = 0;

void mainImage(int fragCoord_x, int fragCoord_y, int *fragColor_r, int *fragColor_g, int *fragColor_b) { // kinda shadertoy naming :)
    float u =  (fragCoord_x -  WIDTH/2.)/HEIGHT;
    float v = -(fragCoord_y - HEIGHT/2.)/HEIGHT;
    float horizon = .32;
    float persp   = 1./((horizon+.05)-v);
    float t  = sin(iTime/4.);
    float t3 = t*t*t;              // cubic law allows for longer straight roads
    float x  = pow(t3 + u*persp - .05*t3*persp*persp, 2.);
    float y  = 2.*persp+20.*iTime; // x,y are texture coordinates
    int dash = sin(y)>0;           // a bit overkill to use sine function here, simple mod/fmod would do well

    if (v>horizon) {
        *fragColor_r = 255*(1.-v); // sunset sky
        *fragColor_g = 128;
        *fragColor_b = 178;
    } else { // actual texture to map
        *fragColor_r = *fragColor_g =  *fragColor_b = 128; // asphalt
        if (x>4.) { // grass
            *fragColor_r = 0;
            *fragColor_g = 178;
            *fragColor_b = 0;
        } else if (x>2.) { // red-white curb
            *fragColor_r = 255;
            *fragColor_g = dash ? 255 : 0;
            *fragColor_b = dash ? 255 : 0;
        } else if (x<.015 && !dash) // central line
            *fragColor_r = *fragColor_g = *fragColor_b = 255;
        *fragColor_r = CLAMP(*fragColor_r*(1-v), 0, 255); // headlights
        *fragColor_g = CLAMP(*fragColor_g*(1-v), 0, 255);
        *fragColor_b = CLAMP(*fragColor_b*(1-v), 0, 255);
    }
}

void multisample(int fragCoord_x, int fragCoord_y) {
    int fragColor_r = 0, fragColor_g = 0, fragColor_b = 0;
    int r, g, b;
    for (int i=0; i<MULTI*MULTI; i++) {
        mainImage(fragCoord_x+i%MULTI, fragCoord_y+i/MULTI, &r, &g, &b);
        fragColor_r += r;
        fragColor_g += g;
        fragColor_b += b;
    }
    printf("%d;%d;%d", fragColor_r/(MULTI*MULTI), fragColor_g/(MULTI*MULTI), fragColor_b/(MULTI*MULTI));
}

int main() {
    printf("\033[2J\033[?25l"); // clear screen and hide cursor
    for (;;) {
        printf("\033[H");       // home
        for (int j = 0; j<HEIGHT/MULTI; j+=2) {
            for (int i = 0; i<WIDTH/MULTI; i++) {
                printf("\033[48;2;"); multisample(i*MULTI, (j+0)*MULTI); printf("m"); // set background color
                printf("\033[38;2;"); multisample(i*MULTI, (j+1)*MULTI); printf("m"); // set foreground color
                printf("\xE2\x96\x83");                                               // half-block Unicode symbol
            }
            printf("\033[49m\n");
        }
        usleep(1000000/FPS);
        iTime += 1./FPS;
    }
    return 0;
}

