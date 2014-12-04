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

#include "splash_img.h"

#pragma config FPLLMUL = MUL_20, FPLLIDIV = DIV_2, FPLLODIV = DIV_1, FWDTEN = OFF
#pragma config POSCMOD = HS, FNOSC = PRIPLL, FPBDIV = DIV_1

#define	GetPeripheralClock()		(SYS_FREQ/(1 << OSCCONbits.PBDIV))

//#define DEBUG

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
#define FRAME_REFRESH_FREQ 50
#define FRAME_REFRESH_CNT  ((SYS_FREQ/2/FRAME_REFRESH_FREQ)-8890)

#define UART_DATA_AVAIL UARTReceivedDataIsAvailable ( UART2 )

#define RSPI_SDO BIT_5
#define RSPI_SCLK BIT_4

#define RDEC_3 BIT_10
#define RDEC_2 BIT_11
#define RDEC_1 BIT_12
#define RDEC_0 BIT_14

//Decoder Mappings
uint8_t rowlu[] = { 3, 2, 1, 0,
                    4, 5, 6, 7,
                    10, 9, 8, 15,
                    11, 12, 13, 14 };

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

void pfbFlushBuffers(void) {
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
inline void pfbDrawRectangle( uint32_t * pfb , uint8_t x0, uint8_t x1, uint8_t y0, uint8_t y1, uint32_t line_colour) {
    uint8_t i, xytmp;
    if( x1 < x0 ) { xytmp = x0; x0=x1; x1=xytmp;}
    if( y1 < y0 ) { xytmp = y0; y0=y1; y1=xytmp;}
    pfbDrawHorizLine(pfb,x0,x1,y0,line_colour);
    pfbDrawHorizLine(pfb,x0,x1,y1,line_colour);
    pfbDrawVertLine(pfb,x0,y0,y1,line_colour);
    pfbDrawVertLine(pfb,x1,y0,y1,line_colour);
}
//TO BE IMPLEMENTED
inline void pfbDrawFilledRectangle( uint32_t * pfb , uint8_t x0, uint8_t x1, uint8_t y0, uint8_t y1, uint32_t line_colour, uint32_t fill_colour) {

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

void apfFlushBuffers(void) {
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
    //Needs to be quick! Use Shifting instead of multiply.
    uint8_t row = 0; //Row of Leds
    uint8_t set = 0; // Set of 4 Leds
    uint32_t i_index_base = 0;
    uint32_t o_index_base = 0;

    for(row = 0; row < 16; row++)
        for (set = 0; set < 4; set++){
            o_index_base = mul25lu[row] + mul6lu[set];
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

    //RX Statemachine
    typedef enum {CMD_SM, DECODE_CMD_SM, DECODE_DRAW_SM, DECODE_STREAM_SM } RxSm_t;
    RxSm_t RxState = CMD_SM;

    //RX Transactions
    //2 Byte Command Transactions {'C', <ENUM>}
    typedef enum {PING_CMD=0, START_DRAW_CMD=1, START_STREAM_CMD=2, FLUSH_BUFFERS_CMD=4,
                  GET_LIGHT_CMD=8, GET_TEMP_CMD=16} RxCmd_t;
    //4 Byte Response Transactions {'R', <ENUM>, VALUE[1:0]}
    typedef enum {PING_RSP=0, ACK_RSP=1, ERR_RSP=2, TEMP_RSP=4, LIGHT_RSP=8} RxRsp_t;
    //8 Byte Draw Transactions {'D', <ENUM>, x0x1, y0y1, COLOUR[3:0]}
    typedef enum {PIXEL_DRAW=0, HLINE_DRAW=1, VLINE_DRAW=2, LINE_DRAW=4, FONT_DRAW=8,
                  RECT_DRAW=16} RxDrawCmd_t; //8Byte


inline uint8_t uartGetByte(void){
   uint8_t a = 0;
   a = UARTGetDataByte(UART2);
   return a;
}
void uartSendRsp(RxRsp_t rspType, uint16_t payload) {
    uint8_t i;
    uint8_t buffer[] = {'R',
                        (uint8_t)rspType,
                        (uint8_t)((payload & 0xFF00)>>8),
                        (uint8_t)(payload & 0x00FF)
                       };

    for (i = 0; i<4;i++) {
       while(!UARTTransmitterIsReady(UART2));
       UARTSendDataByte(UART2, buffer[i]);
    }
}
void uartFlushFifo(void) {
    uint8_t dump;
    while(UARTReceivedDataIsAvailable(UART2))
        dump = UARTGetDataByte(UART2);
}
void uartDebug(uint8_t* mess, uint8_t messLen){
#ifdef DEBUG
    uint8_t i;
    while(!UARTTransmitterIsReady(UART2));
    UARTSendDataByte(UART2,'D');
    while(!UARTTransmitterIsReady(UART2));
    UARTSendDataByte(UART2,':');

    for (i = 0; i<messLen;i++) {
        while(!UARTTransmitterIsReady(UART2));
        UARTSendDataByte(UART2, mess[i]);
    }
    
    //while(!UARTTransmitterIsReady(UART2));
    //UARTSendDataByte(UART2, mess);
    while(!UARTTransmitterIsReady(UART2));
    UARTSendDataByte(UART2, '\r');
    while(!UARTTransmitterIsReady(UART2));
    UARTSendDataByte(UART2, '\n');
#endif
}


uint8_t dcpParse(uint32_t* pfb, uint64_t* dcPtr) {
    uint8_t term = 0;
    uint8_t cmdPre, cmdX0, cmdY0, cmdX1, cmdY1, cmdLet;
    uint32_t cmdCol;
    RxDrawCmd_t cmdType;

    if (*dcPtr == 0xFFFF000000000000) return 1; //MIGHT NEED CORRECTING
    cmdType = (RxDrawCmd_t)(*dcPtr >> 56);
    cmdX0   = (uint8_t)((*dcPtr >> 52) & 0x0F);
    cmdY0   = (uint8_t)((*dcPtr >> 46) & 0x0F);
    cmdX1   = (uint8_t)((*dcPtr >> 40) & 0x0F);
    cmdY1   = (uint8_t)((*dcPtr >> 34) & 0x0F);
    cmdLet  = (uint8_t)((*dcPtr >> 36) & 0xFF);
    cmdCol  = (uint32_t)(*dcPtr & 0xFFFFFFFF);

    switch(cmdType)
    {
        case PIXEL_DRAW: // {PIXEL_DRAW, x0_0y0,y00_x1,0y10, 0xRR0GG0BB}
            pfbDrawPixel (pfb,cmdX0,cmdY0,cmdCol);
            break;
        case HLINE_DRAW: // {HLINE_DRAW, x0_0y0,y00_x1,0000, 0xRR0GG0BB}
            pfbDrawHorizLine (pfb,cmdX0,cmdX1,cmdY0,cmdCol);
            break;
        case VLINE_DRAW: // {VLINE_DRAW, x0_0y0,y00_00,0y10, 0xRR0GG0BB}
            pfbDrawVertLine (pfb,cmdX0,cmdY0,cmdY1,cmdCol);
            break;
        case LINE_DRAW:  // {LINE_DRAW,  x0_0y0,y00_x1,0y10,, 0xRR0GG0BB}
            pfbDrawLine (pfb,cmdX0,cmdX1,cmdY0,cmdY1,cmdCol);
            break;
        case FONT_DRAW:  // {FONT_DRAW,  x0_0y0,y00_L1,L200,  0xRR0GG0BB}
            pfbDrawFont (pfb,cmdX0,cmdX1,cmdLet,cmdCol);
            break;
        case RECT_DRAW:  // {RECT_DRAW,  x0_0y0,y00_x1,0y10, 0xRR0GG0BB}
            pfbDrawRectangle (pfb,cmdX0,cmdX1,cmdY0,cmdY1,cmdCol);
            break;
        default:
            //Do Nothing as unknown command
            break;
    }
    return term;
}

DmaChannel chn0 = DMA_CHANNEL0;
DmaChannel chn1 = DMA_CHANNEL1;
DmaChannel chn2 = DMA_CHANNEL2;
DmaChannel chn3 = DMA_CHANNEL3;
uint8_t    dmaTxComplete = 0;

void dmaStreamSetup( uint32_t* pfb ){
   dmaTxComplete = 0;
   // configure the dma channel chain
   DmaChnOpen(chn0,DMA_CHN_PRI0,DMA_OPEN_DEFAULT);
   DmaChnOpen(chn1,DMA_CHN_PRI0,DMA_OPEN_CHAIN_HI);
   DmaChnOpen(chn2,DMA_CHN_PRI0,DMA_OPEN_CHAIN_HI);
   DmaChnOpen(chn3,DMA_CHN_PRI0,DMA_OPEN_CHAIN_HI);
   //UART2 rx interrupt to start transfer, stops upon detection of 0xFFFF
   DmaChnSetEventControl(chn0, DMA_EV_START_IRQ_EN | DMA_EV_START_IRQ(_UART2_RX_IRQ));
   DmaChnSetEventControl(chn1, DMA_EV_START_IRQ_EN | DMA_EV_START_IRQ(_UART2_RX_IRQ));
   DmaChnSetEventControl(chn2, DMA_EV_START_IRQ_EN | DMA_EV_START_IRQ(_UART2_RX_IRQ));
   DmaChnSetEventControl(chn3, DMA_EV_START_IRQ_EN | DMA_EV_START_IRQ(_UART2_RX_IRQ));
   // set the transfer source and dest addresses, source and dest sizes and the cell size
   DmaChnSetTxfer(chn0, (void*)&U2RXREG, (void*)pfb,     1, 256, 1);
   DmaChnSetTxfer(chn1, (void*)&U2RXREG, (void*)pfb+256, 1, 256, 1);
   DmaChnSetTxfer(chn2, (void*)&U2RXREG, (void*)pfb+512, 1, 256, 1);
   DmaChnSetTxfer(chn3, (void*)&U2RXREG, (void*)pfb+768, 1, 256, 1);
   DmaChnSetEvEnableFlags(chn3, DMA_EV_BLOCK_DONE); // enable the transfer done interrupt: pattern match or all the characters transferred

   // Set up DMA Block Complete interrupt with a priority of 7 and zero sub-priority 
   INTSetVectorPriority(INT_DMA_3_VECTOR, INT_PRIORITY_LEVEL_7);
   INTSetVectorSubPriority(INT_DMA_3_VECTOR, INT_SUB_PRIORITY_LEVEL_0);
   INTEnable(INT_DMA3, INT_ENABLED);

   // Enable multi-vector interrupts
   INTConfigureSystem(INT_SYSTEM_CONFIG_MULT_VECTOR);
   INTEnableInterrupts();
   // enable the chn0 to start the DMA Chain wait
   DmaChnEnable(chn0);
}

void dmaDrawSetup( uint8_t* dcbuff ){
  // configure the channel
  /*  DmaChnOpen(chn, DMA_CHN_PRI2, DMA_OPEN_MATCH);
  //UART2 rx interrupt to start transfer, stops upon detection of 0xFFFF
  DmaChnSetMatchPattern(chn, 0xFFFF); // set \r as ending character
  DCH1CON |= 1<<11;//Dual Byte Match Mode?
  DmaChnSetEventControl(chn, DMA_EV_START_IRQ_EN | DMA_EV_MATCH_EN | DMA_EV_START_IRQ(_UART2_RX_IRQ));
  // set the transfer source and dest addresses, source and dest sizes and the cell size
  DmaChnSetTxfer(chn, (void*) &U2RXREG, dcbuff, 1, sizeof (dcbuff), 1);
  //DmaChnSetEvEnableFlags(chn, DMA_EV_BLOCK_DONE); // enable the transfer done interrupt: pattern match or all the characters transferred
  // enable the chn
  DmaChnEnable(chn);
  */
}


// Hardware Setup
void setupGSCLK(void){
    OpenTimer2(T2_ON, GSCLK_TIM2_CNT);
    OpenOC2( OC_ON | OC_TIMER2_SRC | OC_TOGGLE_PULSE , 0, GSCLK_TIM2_CNT);
}

void setupSPI(void){
    // 32 bits/char, input data sampled at end of data, Try inverted Clock
    SpiOpenFlags oFlags=SPI_OPEN_MODE32 |SPI_OPEN_MSTEN;
    //| SPI_OPEN_CKP_HIGH | SPI_OPEN_CKE_REV;
    // Open SPI module, use SPI channel 1, use flags set above, Divide Fpb by 4
    SpiChnOpen(SPI_CHANNEL2, oFlags, 8);
}

void setupUART(void){
    UARTConfigure(UART2, UART_ENABLE_PINS_TX_RX_ONLY);
    //UARTSetFifoMode(UART2, UART_INTERRUPT_ON_TX_NOT_FULL | UART_INTERRUPT_ON_RX_NOT_EMPTY);
    UARTSetLineControl(UART2, UART_DATA_SIZE_8_BITS | UART_PARITY_NONE | UART_STOP_BITS_1);
    //150465(115200) 299520(230400) 599040(460800)  FUDGE MULT 1.3
    UARTSetDataRate(UART2, GetPeripheralClock(), 599040);
    UARTEnable(UART2, UART_ENABLE_FLAGS(UART_PERIPHERAL | UART_RX | UART_TX));
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
    mPORTEClearBits(BIT_1 | BIT_0 | RSPI_SCLK |RSPI_SDO);
    mPORTESetPinsDigitalOut(BIT_1 | BIT_0 | RSPI_SCLK | RSPI_SDO);

    /* Setup Row Decoder Pins*/
    mPORTBClearBits(RDEC_3 | RDEC_2 | RDEC_1 | RDEC_0);
    mPORTBSetPinsDigitalOut(RDEC_3 | RDEC_2 | RDEC_1 | RDEC_0);
    
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

inline void rowSelector(uint8_t row){
    uint8_t decoder_val = rowlu[row];
    mPORTBClearBits(RDEC_3 | RDEC_2 | RDEC_1 | RDEC_0);
    switch(decoder_val)
    {
        case 0:                                                   break;
        case 1: mPORTBSetBits(RDEC_0);                            break;
        case 2: mPORTBSetBits(RDEC_1);                            break;
        case 3: mPORTBSetBits(RDEC_1 | RDEC_0);                   break;
        case 4: mPORTBSetBits(RDEC_2);                            break;
        case 5: mPORTBSetBits( RDEC_2 | RDEC_0);                  break;
        case 6: mPORTBSetBits( RDEC_2 | RDEC_1);                  break;
        case 7: mPORTBSetBits( RDEC_2 | RDEC_1 | RDEC_0);         break;
        case 8: mPORTBSetBits(RDEC_3);                            break;
        case 9: mPORTBSetBits(RDEC_3 | RDEC_0);                   break;
        case 10: mPORTBSetBits(RDEC_3 |RDEC_1 );                  break;
        case 11: mPORTBSetBits(RDEC_3 | RDEC_1 | RDEC_0);         break;
        case 12: mPORTBSetBits(RDEC_3 | RDEC_2 );                 break;
        case 13: mPORTBSetBits(RDEC_3 | RDEC_2 | RDEC_0);         break;
        case 14: mPORTBSetBits(RDEC_3 | RDEC_2 | RDEC_1);         break;
        case 15: mPORTBSetBits(RDEC_3 | RDEC_2 | RDEC_1 | RDEC_0);break;
        default:                                                  break;

    }
}

inline void uint32Str(uint32_t val, char* buff){
    //char tmp [9];
    itoa (val, buff, 16);
    //strncpy(tmp, buff, 8);
}

// Row Refresh Interrupt Handler
void __ISR(_TIMER_4_VECTOR, ipl6) Timer4Handler(void) {
    uint32_t t = 1;
    uint32_t l = 0;
    uint32_t b = mul25lu[ApfNextRow+1]-1;

    INTClearFlag(INT_T4);                               // Clear the interrupt flag

    for(t=1; t < 25; t++)
    {
      SpiChnPutC(SPI_CHANNEL2,Apf[ApfActiveFrame][b-t]);// Send SPI Data
    }

    while(SpiChnIsBusy(SPI_CHANNEL2));                  //Wait Till SPI Done

    mPORTESetBits(BIT_1 | BIT_0);                               //Set XLAT/Blank Signal
    rowSelector(ApfNextRow);                                    //Decoder Row Selector

    if ((ApfSwitchPending == 1) && (ApfNextRow >= 15)) {       //EoR & Switch Pending
        ApfActiveFrame = (ApfActiveFrame) ? 0 : 1;
        ApfSwitchPending = 0;
    }
    
    ApfNextRow = (ApfNextRow >= 15) ? 0: ApfNextRow+1;  //Increment to Next Row

    for(l=0;l<5;l++) mPORTESetBits(BIT_1 | BIT_0);//AntiFlicker
    mPORTEClearBits(BIT_1 | BIT_0);                             //Clear XLAT/Blank Signal

}

// Frame Refresh Interrupt Handler
void __ISR(_TIMER_3_VECTOR, ipl5) Timer3Handler(void) {
    uint32_t i = 0;
    uint32_t lastPfb = 0;
    uint32_t ApfToFill = (ApfActiveFrame) ? 0 : 1;
    //mPORTEToggleBits(BIT_1 | BIT_0);

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

// DMA3 Block Complete Interrupt Handler
void __ISR(_DMA_3_VECTOR, ipl7) DMA3Handler(void) {
    dmaTxComplete = 1;
    INTClearFlag(INT_DMA3);                               // Clear the interrupt flag
}


int main(void) {

    SYSTEMConfig(SYS_FREQ, SYS_CFG_WAIT_STATES |SYS_CFG_PCACHE);
    mJTAGPortEnable(DEBUG_JTAGPORT_OFF);

    /* Setup UART Interface to RaspberryPi*/
    setupUART();

    uartDebug("Booting Up...",13);

    pfbFlushBuffers();
    apfFlushBuffers();

    apfPack(splash_hackaday, Apf[0]); // Load Debug PFB into APF
    /* Setup GSCLK using TIMER2 & OC2 */
    setupGSCLK();
    /* Setup SPI Interface to LED Matrix*/
    setupSPI();
    /*Setup RowRefresh Clk TIMER4 */
    setupRowRefresh();
    /*Setup Buffer Refresh*/
    setupFrameRefresh();
    
    uartDebug("Initialization Complete",23);


    RxRsp_t RxRsp;
    uint16_t RxRspValue;
    uint8_t DcBuffer8[1024];
    uint64_t* DcBuffer64;
    uint32_t tmpPix;
    uint16_t i,j;

    while(1) {
        tmpPix = 0;
        i = 0;

        switch (RxState) {
            case CMD_SM:
                if (UART_DATA_AVAIL) {
                    while (PfbFull); // Wait till there is space in PFB
                    RxState = DECODE_CMD_SM;
                }
                break;

            case DECODE_CMD_SM:
                if (uartGetByte() == 'C') {
                    while(!UART_DATA_AVAIL);
                    switch((RxCmd_t)uartGetByte()) {
                        case PING_CMD:
                            uartDebug("Rx Ping Command",15);
                            RxRsp = PING_RSP;
                            RxRspValue = ('Z'<<8)|'X';
                            RxState = CMD_SM;
                            break;
                        case START_DRAW_CMD:
                            uartDebug("Rx Start Draw Command",21);
                            RxRsp = ACK_RSP;
                            RxRspValue = 0x0000;
                            RxState = DECODE_DRAW_SM;
                            break;
                        case START_STREAM_CMD:
                            uartDebug("Rx Start Stream Command",23);
                            RxRsp = ACK_RSP;
                            RxRspValue = 0x0000;
                            RxState = DECODE_STREAM_SM;
                            break;
                        case FLUSH_BUFFERS_CMD:
                            uartDebug("Rx Flush Command",16);
                            RxRsp = ACK_RSP;
                            RxRspValue = 0x0000;
                            pfbFlushBuffers();
                            apfFlushBuffers();
                            RxState = CMD_SM;
                            break;
                        case GET_LIGHT_CMD:
                            uartDebug("Rx Light Command",16);
                            RxRsp = LIGHT_RSP;
                            RxRspValue = 0x1234; // TODO
                            RxState = CMD_SM;
                            break;
                        case GET_TEMP_CMD:
                            uartDebug("Rx Temp Command",15);
                            RxRsp = TEMP_RSP;
                            RxRspValue = 0x5678; // TODO
                            RxState = CMD_SM;
                            break;
                        default:
                            uartDebug("Rx Invalid Command",18);
                            RxRsp = ERR_RSP;
                            RxRspValue = ('I'<<8)|'C'; //Invalid Command
                            RxState = CMD_SM;
                            break;
                    }
                    uartSendRsp(RxRsp,RxRspValue);
                    } else {
                        uartSendRsp(ERR_RSP, (('X'<<8)|'X') );
                        uartFlushFifo();
                        RxState = CMD_SM;
                    }
                    break;
                case DECODE_DRAW_SM:
                    i = 0;
                    //dmaDrawSetup( DcBuffer8 );
                    uartDebug("Dma Draw Setup",14);
                    //while(DCH1CON | (1<<15) );//while DMA is running
                    DcBuffer64 = (uint64_t*) DcBuffer8;
                    uartDebug("Dma Draw Complete",17);
                    //while (dcpParse(Pfb[PfbNextFree],&DcBuffer64[i]) == 0) i++;
                    uartDebug("DCP Parse Complete",18);
                    //pfbPush();
                    RxState = CMD_SM;
                    break;
                case DECODE_STREAM_SM:
                    dmaStreamSetup( Pfb[PfbNextFree] );
                    uartDebug("Dma Stream Setup",16);
                    /*uint8_t fEnAct = 0;
                    uint8_t fEvent0 = 0;
                    uint8_t fEvent1 = 0;
                    uint8_t fEvent2 = 0;
                    uint8_t fEvent3 = 0;*/

                    uint8_t fCp0 = 0;
                    uint8_t fCp1 = 0;
                    char valStr [9];
                    uint32Str((void*)Pfb[PfbNextFree], valStr); //Print Pfb Pointer
                    uartDebug(valStr,8);
                    while(dmaTxComplete == 0){
                       /* if ((fEnAct == 0) && (DMACON & 0x00008800)) {
                            uartDebug("Dma Module Enabled & Active",27);
                            fEnAct = 1;
                        }

                        if ((fEvent0 == 0) && (DCH0CON & 0x00008004)) {
                            uartDebug("Dma CH0 Event",13);
                            fEvent0 = 0;
                        }
                        if ((fEvent1 == 0) && (DCH1CON & 0x00008004)) {
                            uartDebug("Dma CH1 Event",13);
                            fEvent1 = 0;
                            if (~DCH0CON & 0x00008000){
                                uartDebug("Dma CH0 Inactive",17);
                            }
                        }
                        if ((fEvent2 == 0) && (DCH2CON & 0x00008004)) {
                            uartDebug("Dma CH2 Event",13);
                            fEvent2 = 0;
                            if (~DCH1CON & 0x00008000){
                                uartDebug("Dma CH1 Inactive",17);
                            }
                        }
                        if ((fEvent3 == 0) && (DCH3CON & 0x00008004)) {
                            uartDebug("Dma CH3 Event",13);
                            fEvent3 = 0;
                            if (~DCH2CON & 0x00008000){
                                uartDebug("Dma CH2 Inactive",17);
                            }
                        }

                        if ((fCp0 == 0) && (DCH0CPTR > 0)) {
                            uartDebug("Dma CH0 PTR > 0",15);
                            fCp0 = 1;
                        }
                        if ((fCp1 == 0) && (DCH0CPTR > 128)) {
                            uartDebug("Dma CH0 PTR > 128",17);
                            fCp1 = 1;
                        }*/
                    };
                    uartDebug("Dma Stream Complete",19);

                    //Kludge -- Replace with DMA to speed up!
                    //for(i=0; i<256; i++){
                    //    tmpPix = 0;
                    //   for(j=0; j<3; j++) {
                    //       while(!UART_DATA_AVAIL);
                    //       tmpPix |= ((uint32_t)UARTGetDataByte(UART2)) << j*12;
                    //    }
                    //    Pfb[PfbNextFree][i] = tmpPix;
                    //}

                    //uartPFBPrint
                    pfbPush();
                    uartSendRsp(ACK_RSP,0x0001);
                    RxState = CMD_SM;
                    //uartDebug("End Stream",10);
                    break;
                default:
                    uartDebug("Bad State",9);
                    RxState = CMD_SM; //Reset SM
                    break;
            }
    }
    return (EXIT_SUCCESS);
}


