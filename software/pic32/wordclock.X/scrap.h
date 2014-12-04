/* 
 * File:   scrap.h
 * Author: matt
 *
 * Created on 26 July 2014, 21:05
 */

#ifndef SCRAP_H
#define	SCRAP_H

#ifdef	__cplusplus
extern "C" {
#endif

        int mode_block = 0;
    int led_i = 0;
    int led_pos = 0;
    int led_color = 0;
    int led_color_arr[] = {0x000000FF, 0x000FF000, 0xFF000000, 0xFF0FF0FF};
    
      }

        if (mode_num == 5) {}
        if (mode_num == 3 && mode_block < 1) {
           pfbDrawVertLine(Pfb[PfbNextFree],0,15,0,0x0000F000);
           pfbDrawVertLine(Pfb[PfbNextFree],1,15,0,0x0000E00);
           pfbDrawVertLine(Pfb[PfbNextFree],2,15,0,0x0000D000);
           pfbDrawVertLine(Pfb[PfbNextFree],3,15,0,0x0000C00);
           pfbDrawVertLine(Pfb[PfbNextFree],4,15,0,0x0000B000);
           pfbDrawVertLine(Pfb[PfbNextFree],5,15,0,0x0000A000);
           pfbDrawVertLine(Pfb[PfbNextFree],6,15,0,0x00009000);
           pfbDrawVertLine(Pfb[PfbNextFree],7,15,0,0x00008000);
           pfbDrawVertLine(Pfb[PfbNextFree],8,15,0,0x00007000);
           pfbDrawVertLine(Pfb[PfbNextFree],9,15,0,0x00006000);
           pfbDrawVertLine(Pfb[PfbNextFree],10,15,0,0x00005000);
           pfbDrawVertLine(Pfb[PfbNextFree],11,15,0,0x00004000);
           pfbDrawVertLine(Pfb[PfbNextFree],12,15,0,0x00003000);
           pfbDrawVertLine(Pfb[PfbNextFree],13,15,0,0x00002000);
           pfbDrawVertLine(Pfb[PfbNextFree],14,15,0,0x00001000);
           pfbDrawVertLine(Pfb[PfbNextFree],15,15,0,0x00000000);

           pfbPush();
           ++mode_block;
        } else if (mode_num == 0 && mode_block < 1) {
        pfbDrawVertLine(Pfb[PfbNextFree],0,15,10,0x000FF000);
        pfbDrawVertLine(Pfb[PfbNextFree],0,9,7,0xFF0FF000);
        pfbDrawPixel(Pfb[PfbNextFree]   ,0,6,0xFF000000);

        pfbDrawVertLine(Pfb[PfbNextFree],2,15,10,0x000FF000);
        pfbDrawVertLine(Pfb[PfbNextFree],2,9,7,0xFF0FF000);
        pfbDrawPixel(Pfb[PfbNextFree]   ,2,6,0xFF000000);

        pfbDrawVertLine(Pfb[PfbNextFree],4,15,10,0x000FF000);
        pfbDrawVertLine(Pfb[PfbNextFree],4,9,7,0xFF0FF000);
        pfbDrawPixel(Pfb[PfbNextFree]   ,4,6,0xFF000000);

        pfbDrawVertLine(Pfb[PfbNextFree],6,15,10,0x000FF000);
        pfbDrawVertLine(Pfb[PfbNextFree],6,9,7,0xFF0FF000);
        pfbDrawPixel(Pfb[PfbNextFree]   ,6,6,0xFF000000);

        pfbDrawVertLine(Pfb[PfbNextFree],8,15,10,0x000FF000);
        pfbDrawVertLine(Pfb[PfbNextFree],8,9,7,0xFF0FF000);
        pfbDrawPixel(Pfb[PfbNextFree]   ,8,6,0xFF000000);

        pfbDrawVertLine(Pfb[PfbNextFree],10,15,10,0x000FF000);
        pfbDrawVertLine(Pfb[PfbNextFree],10,9,7,0xFF0FF000);
        pfbDrawPixel(Pfb[PfbNextFree]   ,10,6,0xFF000000);

        pfbDrawVertLine(Pfb[PfbNextFree],12,15,10,0x000FF000);
        pfbDrawVertLine(Pfb[PfbNextFree],12,9,7,0xFF0FF000);
        pfbDrawPixel(Pfb[PfbNextFree]   ,12,6,0xFF000000);

        pfbDrawVertLine(Pfb[PfbNextFree],14,15,10,0x000FF000);
        pfbDrawVertLine(Pfb[PfbNextFree],14,9,7,0xFF0FF000);
        pfbDrawPixel(Pfb[PfbNextFree]   ,14,6,0xFF000000);

        pfbPush();
        ++mode_block;

        } else if ( mode_num == 1 && mode_block < 1) {
           while( PfbFull == 0 ) {
           //Cycle LEDs and colours

           //0, 12, 24
           Pfb[PfbNextFree][led_pos] = led_color_arr[led_color];
           pfbPush() ;
           ++led_pos;
           led_color = (led_pos > 255) ? led_color + 1 : led_color;
           led_pos   = (led_pos > 255) ? 0 : led_pos; // Led rollover
           led_color = (led_color > 3) ? 0 : led_color;
           }
        } else if ( mode_num == 2 && mode_block < 1) {
            while( PfbFull == 0 ) {
           //Cycle Line Colours

            for (led_i = 0; led_i < 16; ++led_i)
              Pfb[PfbNextFree][led_pos + led_i] = led_color_arr[led_color];
            pfbPush() ;
            led_pos = led_pos + 16;
            led_color = (led_pos > 255) ? led_color + 1 : led_color;
            led_pos   = (led_pos > 255) ? 0 : led_pos; // Led rollover
            }
    } else if ( mode_num == 4 && mode_block < 1) {
        led_color = 1;
            while( PfbFull == 0 ) {
           //Led Dimming
              Pfb[PfbNextFree][120] = led_color << 12;
              Pfb[PfbNextFree][50] = led_color << 12;
              Pfb[PfbNextFree][10] = led_color << 12;
              Pfb[PfbNextFree][190] = led_color << 12;
              pfbPush() ;
              led_color = led_color << 1; // Switch Direction
              if (led_color > 128 ) ++mode_block;

            }
    }




#ifdef	__cplusplus
}
#endif

#endif	/* SCRAP_H */

