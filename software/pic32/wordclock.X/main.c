/* 
 * File:   main.c
 * Author: matt
 *
 * Created on 08 June 2014, 15:38
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <plib.h>


#pragma config FPLLMUL = MUL_20, FPLLIDIV = DIV_2, FPLLODIV = DIV_1, FWDTEN = OFF
#pragma config POSCMOD = HS, FNOSC = PRIPLL, FPBDIV = DIV_1

#define DEBUG 1

#define SYS_FREQ (80000000L)

//Frequency Definitions
#define LED_FREQ       100
#define ROW_REFRESH_FREQ   (LED_FREQ*16)
//Another Extra Offset...WTF 6000-> 1.579kHz, 5000 -> 1.5kHz, 4500->
#define ROW_REFRESH_CNT    ((SYS_FREQ/2/ROW_REFRESH_FREQ)-4500)
#define GSCLK_FREQ     (ROW_REFRESH_FREQ*256)
//Extra Offset needed to get 406Khz, weird
#define GSCLK_TIM2_CNT ((SYS_FREQ/2/GSCLK_FREQ)-18)

//Refresh Definitions
#define FRAME_REFRESH_FREQ 3
#define FRAME_REFRESH_CNT  ((SYS_FREQ/2/FRAME_REFRESH_FREQ)-4500)

#ifdef DEBUG
#include "debug_pfb.h"
#endif

//Mul25 Lookup array to avoid Multiplies
uint32_t mul25lu[] = {  0,  25,  50,  75,
                      100, 125, 150, 175,
                      200, 225, 250, 275,
                      300, 325, 350, 375,
                      400 };

uint32_t mul16lu[] = {  0,  16,  32,  48,
                       64,  80,  96, 112,
                      128, 144, 160, 176,
                      192, 208, 224, 240,
                      256 };

//Mul6 Lookup Array to avoid Multiplies
uint32_t mul6lu[] = {  0,  6,  12,  18};

/* UnpaddedFrameBuffer Upfb[N][256]
 * Holds N *Compressed* Frames at a time straight from UART
 * Each Frame contains 256 * 32bit words in the format:
 *
 * 31                           0
 *  -----------------------------
 *  |  Rn  |0x0|  Gn  |0x0| Bn  |
 *  -----------------------------
 *     8b   4b   8b    4b   8b
 *
 * Each 32bit word is a pixel, where index   0 -> 15 is row one
 *                                   index 240 -> 255 is row 16
 *
 * Pfb         : Two Dimensional Array containing the Data
 * PfbCount    : Number of valid Entries in PFB
 * PfbNextFree : Points to the next free empty in the Pfb
 * PfbHead     : Head of the Pfb, next to be filled into none active frame
 * PfbFull     : Is Pfb Buffer Full
 */
#define PFB_FRAMES 10

uint8_t  PfbFull = 0;
uint8_t  PfbNextFree = 0;
uint8_t  PfbHead = 0;
uint8_t  PfbCount = 0;
uint32_t Pfb [PFB_FRAMES][256];

void pfbInitBuffers(void) {
uint32_t i = 0; uint32_t j = 0;

//Init and Clear Pfb
PfbNextFree = 0;
PfbHead = 0;
PfbFull = 0;
PfbCount = 0;

for (i = 0; i < PFB_FRAMES; i++)
    for (j =0; j < 256; j++)
        Pfb[i][j] = 0;
}

void pfbPush(void) {
    int tmpNext;
    //Choose Next Free Slot
    tmpNext = PfbNextFree + 1;
    PfbNextFree = (tmpNext == PFB_FRAMES) ? 0 : tmpNext; // Roll Round
    //PfbFull = (PfbNextFree == PfbHead) ? 1 : 0; // If tmpNext is valid then full
    ++PfbCount; //Increment Count
    PfbFull = (PfbCount >= PFB_FRAMES) ? 1 : 0; // If PfbCount == PFB_FRAMES then Full
}

void pfbPop(void) {
    int tmpHead;
    //Choose Next Free Slot
    tmpHead = PfbHead + 1;
    PfbHead = (tmpHead == PFB_FRAMES) ? 0 : tmpHead; // Roll Round
    --PfbCount; //Increment Count
    PfbFull = (PfbCount >= PFB_FRAMES) ? 1 : 0; // If PfbCount == PFB_FRAMES then Full
}

void pfbDrawPixel( uint32_t * pfb , uint8_t x, uint8_t y, uint32_t colour) {
    pfb[mul16lu[y]+x] = colour;
}

inline void pfbDrawVertLine( uint32_t * pfb , uint8_t x, uint8_t y0, uint8_t y1, uint32_t colour) {
    uint8_t i, ytmp;
    if( y1 < y0 ) { ytmp = y0; y0=y1; y1=ytmp;}
    for(i=y0; i<=y1; i++)
        pfb[mul16lu[i]+x] = colour;
}

inline void pfbDrawHorizLine( uint32_t * pfb , uint8_t x0, uint8_t x1, uint8_t y, uint32_t colour) {
    uint8_t i, xtmp;
    uint32_t y_base = mul16lu[y];
    if( x1 < x0 ) { xtmp = x0; x0=x1; x1=xtmp;}
    for(i=x0; i<=x1; i++)
        pfb[y_base+i] = colour;
}

//TO BE IMPLEMENTED
inline void pfbDrawLine( uint32_t * pfb , uint8_t x0, uint8_t x1, uint8_t y0, uint8_t y1, uint32_t colour) {

}
//TO BE IMPLEMENTED
inline void pfbDrawRectangle( uint32_t * pfb , uint8_t x0, uint8_t x1, uint8_t y0, uint8_t y1, uint32_t line_colour, uint32_t fill_colour) {

}
//TO BE IMPLEMENTED
inline void pfbDrawFont( uint32_t * pfb , uint8_t x0, uint8_t x1, uint8_t letter, uint32_t colour) {

}

/*ActivePaddedFrames
 * Holds 2 *Uncompressed* Frames ready to be sent via SPI to LED Matrix
 * This takes into account all the extra padding needed for unused PWM channels
 * and extra 4 precisions bit padding per LED. There are two of these Frames,
 * One active being used to drive the Display, The other is being filled if Pfb is not empty
 * 
 * where R = NextRow to SPI 
 * Row Data can be found between 25R -> 25R+23,
 * Row Select can be found in    25R+24,
 *
 *
 * Apf            : Two Dimensional Array containing the uncompressed data.
 * ApfNextRow     : The next row to be sent via SPI from the Active Frame
 * ApfActiveFrame : Which of the two ActivePaddedFrames is currently displayed
 */
uint8_t  ApfActiveFrame = 0;
uint8_t  ApfNextRow = 0;
uint8_t  ApfSwitchPending = 0;
uint32_t Apf [2][400];

void apfInitBuffers(void) {
uint32_t i = 0; uint32_t j = 0; uint32_t row = 0; uint32_t row_reord = 0 ;

//Init and Clear Apf
ApfActiveFrame = 0;
ApfNextRow = 0;
ApfSwitchPending = 0;
for (i = 0; i < 2; i++)
    for (j = 0; j < 400; j++)
        Apf[i][j] = 0;

//Iterate Through Apfs and set Row Selects as they stay constant
for (i = 0; i<2; i++)
    for (row = 0; row <16; row++)
    {
        // Reorder Row select values due to wiring order
        if (row < 4)        row_reord = row+12;
        else if (row < 8)   row_reord = row+4;
        else if (row <12)   row_reord = row-4;
        else                row_reord = row-12;

        Apf[i][(mul25lu[row])+24] = ~(1<<row_reord) | 0xFFFF0000;
    }
}

void apfPack(uint32_t* unpadded_i, uint32_t* padded_o) {
    //Needs to be quick! Use Shifting & Multiply instead of multiply.
    uint8_t row = 0; //Row of Leds
    uint8_t set = 0; // Set of 4 Leds
    uint32_t i_index_base = 0;
    uint32_t o_index_base = 0;

    for(row = 0; row < 16; row++)
        for (set = 0; set < 4; set++){
            o_index_base = mul25lu[row] + mul6lu[set];

            //i_index_base = (((row+1)<<4)-1) - (set<<2); //16*row + 4*set
            //padded_o[o_index_base]    = unpadded_i[i_index_base];
            //padded_o[o_index_base+1]  = unpadded_i[i_index_base+1] << 4;
            //padded_o[o_index_base+2]  = unpadded_i[i_index_base+1] >> 28;
            //padded_o[o_index_base+2] |= unpadded_i[i_index_base+2] << 8;
            //padded_o[o_index_base+3]  = unpadded_i[i_index_base+2] >> 24;
            //padded_o[o_index_base+3] |= unpadded_i[i_index_base+3] << 12;
            //padded_o[o_index_base+4]  = unpadded_i[i_index_base+3] >> 20;

            i_index_base = (row<<4) + (set<<2);
            padded_o[o_index_base]    = unpadded_i[i_index_base+3];
            padded_o[o_index_base+1]  = unpadded_i[i_index_base+2] << 4;
            padded_o[o_index_base+2]  = unpadded_i[i_index_base+2] >> 28;
            padded_o[o_index_base+2] |= unpadded_i[i_index_base+1] << 8;
            padded_o[o_index_base+3]  = unpadded_i[i_index_base+1] >> 24;
            padded_o[o_index_base+3] |= unpadded_i[i_index_base] << 12;
            padded_o[o_index_base+4]  = unpadded_i[i_index_base] >> 20;
        }

}


// Hardware Setup
void setupGSCLK(void){
    OpenTimer2(T2_ON, GSCLK_TIM2_CNT);
    OpenOC2( OC_ON | OC_TIMER2_SRC | OC_TOGGLE_PULSE , 0, GSCLK_TIM2_CNT);
}

void setupSPI(void){
    // 32 bits/char, input data sampled at end of data output time
    SpiOpenFlags oFlags=SPI_OPEN_MODE32 |SPI_OPEN_MSTEN;
    // Open SPI module, use SPI channel 1, use flags set above, Divide Fpb by 4
    SpiChnOpen(SPI_CHANNEL2, oFlags, 8);
}

void setupFrameRefresh(void){
    // Configure Timer 3
    OpenTimer3(T3_ON | T3_PS_1_256, FRAME_REFRESH_CNT);

    // Set up Timer 3 interrupt with a priority of 6 and zero sub-priority
    INTEnable(INT_T3, INT_ENABLED);
    INTSetVectorPriority(INT_TIMER_3_VECTOR, INT_PRIORITY_LEVEL_5);
    INTSetVectorSubPriority(INT_TIMER_3_VECTOR, INT_SUB_PRIORITY_LEVEL_0);

    // Enable multi-vector interrupts
    INTConfigureSystem(INT_SYSTEM_CONFIG_MULT_VECTOR);
    INTEnableInterrupts();
}

void setupRowRefresh(void){

    /* Setup Ports for XLAT & BLANK*/
    mPORTEClearBits(BIT_1 | BIT_0);
    mPORTESetPinsDigitalOut(BIT_1 | BIT_0);
    
    // Configure Timer 4
    OpenTimer4(T4_ON | T4_PS_1_2, ROW_REFRESH_CNT);

    // Set up Timer 4 interrupt with a priority of 6 and zero sub-priority
    INTEnable(INT_T4, INT_ENABLED);
    INTSetVectorPriority(INT_TIMER_4_VECTOR, INT_PRIORITY_LEVEL_6);
    INTSetVectorSubPriority(INT_TIMER_4_VECTOR, INT_SUB_PRIORITY_LEVEL_0);

    // Enable multi-vector interrupts
    INTConfigureSystem(INT_SYSTEM_CONFIG_MULT_VECTOR);
    INTEnableInterrupts();
}

// Row Refresh Interrupt Handler
void __ISR(_TIMER_4_VECTOR, ipl6) Timer4Handler(void) {
    uint32_t t = 0;
    uint32_t b = mul25lu[ApfNextRow+1]-1;

    INTClearFlag(INT_T4);                               // Clear the interrupt flag
    //mPORTESetBits(BIT_0);                               //Set BLANK Signal

    for(t=0; t < 25; t++)
    {
      SpiChnPutC(SPI_CHANNEL2,Apf[ApfActiveFrame][b-t]);// Send SPI Data
    }

    while(SpiChnIsBusy(SPI_CHANNEL2));                  //Wait Till SPI Done

    mPORTESetBits(BIT_1 | BIT_0);                               //Set XLAT/Blank Signal

    if ((ApfSwitchPending == 1) && (ApfNextRow >= 15)) {       //EoR & Switch Pending
        ApfActiveFrame = (ApfActiveFrame) ? 0 : 1;
        ApfSwitchPending = 0;
    }
    mPORTEClearBits(BIT_1 | BIT_0);                             //Clear XLAT/Blank Signal

    ApfNextRow = (ApfNextRow >= 15) ? 0: ApfNextRow+1;  //Increment to Next Row

}

// Frame Refresh Interrupt Handler
void __ISR(_TIMER_3_VECTOR, ipl5) Timer3Handler(void) {
    uint32_t i = 0;
    uint32_t lastPfb = 0;
    uint32_t ApfToFill = (ApfActiveFrame) ? 0 : 1;

    INTClearFlag(INT_T3);                               // Clear the interrupt flag

    //If Pfb isn't empty and Switch not pending then convert and pop.
    if ( (PfbCount > 0) && (ApfSwitchPending == 0) )  {
        apfPack(Pfb[PfbHead], Apf[ApfToFill]);
        lastPfb = PfbHead;
        pfbPop();
        ApfSwitchPending = 1;
        ///////////////////////////////////////
        for (i = 0; i < 256; i++)
            Pfb[lastPfb][i] = 0;
        ///////////////////////////////////////
    }

}



int main(void) {

    SYSTEMConfig(SYS_FREQ, SYS_CFG_WAIT_STATES |SYS_CFG_PCACHE);
    mJTAGPortEnable(DEBUG_JTAGPORT_OFF);

    pfbInitBuffers();
    apfInitBuffers();

    apfPack(debug_pfb, Apf[0]); // Load Debug PFB into APF
    /* Setup GSCLK using TIMER2 & OC2 */
    setupGSCLK();
    /* Setup SPI Interface to LED Matrix*/
    setupSPI();
    /*Setup RowRefresh Clk TIMER4 */
    setupRowRefresh();

    /*Setup Buffer Refresh*/
    setupFrameRefresh();

    int mode_num = 5;
    int mode_block = 0;
    int led_i = 0;
    int led_pos = 0;
    int led_color = 0;
    int led_color_arr[] = {0x000000FF, 0x000FF000, 0xFF000000, 0xFF0FF0FF};
    
    while(1)
    {
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



    }

    return (EXIT_SUCCESS);
}


