#include <stdio.h>
#include <stdbool.h>
#include <unistd.h> // for usleep()

#define ABS(a) (((a) < 0) ? -(a) : (a))
#define CLAMP(x, low, high) (((x) > (high)) ? (high) : (((x) < (low)) ? (low) : (x)))

const char* palette[2] = { "187;204;51", "213;48;49" };
struct Ball { int x[2], v[2]; } balls[2];
bool bricks[48*48]; // The battlefield. The brick grid is 16x16, but it is zoomed x4 for more fluid motion

int xor_bricks(int x, int y, bool ball) { // flip a 4x4 block of the battlefield
    int hit = -1;                         // N.B. the block is not aligned to the brick grid
    for (int i=0; i<16; i++) {
        int idx = x+i%4+(y+i/4)*48;
        if ((bricks[idx] ^= true) == ball) hit = idx; // if a ball hits a brick, return the brick position
    }
    return hit;
}

int main() {
    balls[0].x[0] =  3; balls[0].x[1] =  3; // initial position and speed for two balls
    balls[0].v[0] =  1; balls[0].v[1] =  3;
    balls[1].x[0] = 41; balls[1].x[1] = 43;
    balls[1].v[0] = -1; balls[1].v[1] = -3;

    for (int i=0; i<48*48; i++)
        bricks[i] = i<48*48/2; // initialize the battlefield

    printf("\033[2J"); // clear screen
    for (;;) {
        printf("\033[H"); // home
        for (int b=0; b<2; b++) // for each ball
            for (int d=0; d<2; d++ ) // for each coordinate
                for (int i=0; i<ABS(balls[b].v[d]); i++) { // move the ball one step at a time
                    balls[b].x[d] += balls[b].v[d] > 0 ? 1 : -1;
                    if (balls[b].x[d]<0 || balls[b].x[d]>48-4) { // bounce the ball off the walls
                        balls[b].x[d] = CLAMP(balls[b].x[d], 0, 48-4);
                        balls[b].v[d] = -balls[b].v[d];
                    }
                    int hit = xor_bricks(balls[b].x[0], balls[b].x[1], !b); // draw the ball and check if it hits a brick
                    xor_bricks(balls[b].x[0], balls[b].x[1], !b);           // immediately clear the ball
                    if (hit!=-1) { // if we hit a brick
                        xor_bricks(((hit%48)/4)*4, ((hit/48)/4)*4, !b); // snap the hit to the brick grid and break the brick
                        balls[b].v[d] = -balls[b].v[d];                 // bounce the ball off the brick
                        balls[b].x[d] += balls[b].v[d] > 0 ? 1 : -1;
                    }
                }

        for (int b=0; b<2; b++)     // imprint the balls into the battlefield
            xor_bricks(balls[b].x[0], balls[b].x[1], !b);
        for (int j=0; j<48; j+=2) { // show the battlefield
            for (int i=0; i<48; i++) {
                printf("\033[48;2;%sm",palette[bricks[i + (j+0)*48]]); // set background color
                printf("\033[38;2;%sm",palette[bricks[i + (j+1)*48]]); // set foreground color
                printf("\xE2\x96\x83");                                // half-block Unicode symbol
            }
            printf("\033[49m\n");
        }
        for (int b=0; b<2; b++)     // clear the balls from the battlefield
            xor_bricks(balls[b].x[0], balls[b].x[1], !b);
        usleep(1000000/50); // fps
    }
    return 0;
}

