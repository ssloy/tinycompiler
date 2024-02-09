#include <stdio.h>
#include <string.h>
#include <stdint.h>

int main() {
    char c[] = ".,'~=+:;[/<&?oxOX# ";
    int32_t l = strlen(c);

    int32_t w = 80;
    int32_t h = 25;
    int32_t s = 1<<13;

    for (int32_t y=0; y<h; y++) {
        int32_t r = -(125*s)/100 + ((25*s/10)*y)/h;
        for (int32_t x=0; x<w; x++) {
            int32_t v = -2*s + ((25*s/10)*x)/w;
            int32_t d = 0;
            int32_t e = 0;
            int32_t a = -1;

            while (a<l-1 && d*d+e*e<4*s*s) {
                int32_t z = (d*d-e*e)/s+v;
                e = (d+d)*e/s + r;
                d = z;
                a++;
            }
            printf("%c", c[a]);
        }
        printf("\n");
    }
    return 0;
}

