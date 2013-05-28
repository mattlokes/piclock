#include "stm32f10x.h"
#include "stm32f10x_tim.h"
#include "spi.h"

// ------- DEFINES -------------------
#define DEBUGLED0 8 //PC8 - DEBUGLED0
#define DEBUGLED1 9 //PC9 - DEBUGLED1

#define VPRG 0      //PA0 OUT
#define XLAT 1      //PA1 OUT
#define BLANK 2     //PA2 OUT
#define DCPRG 3     //PA3 OUT
#define GSCK 0      //PB0 OUT
#define SPI1_SCK 5  //PA5 OUT
#define SPI1_MISO 6 //PA6 OUT
#define SPI1_MOSI 7 //PA7 IN

//------------ MACROS ------------------
#define CRH_MODE(M,N)   (M<<(4*(N-8)))
#define CRL_MODE(M,N)   (M<<(4*(N)))
#define CRH_MODE_OUT(N) (CRH_MODE(3,N))
#define CRL_MODE_OUT(N) (CRL_MODE(3,N))

#define OUT_ON(P,N)     P->BSRR = (1<<N);
#define OUT_OFF(P,N)    P->BRR = (1<<N);
#define OUT_FLIP(P,N)   P->ODR ^= (1<<N);
//---------------------------------------

//  Declare Frame Buffer
volatile uint8_t framebuff[4][24];

void assert_failed(uint8_t* file, uint32_t line)
{
}

void ms_delay(int ms)
{
   while (ms-- > 0) {
      volatile int x=5971;
      while (x-- > 0)
         __asm("nop");
   }
}

void us_delay(int us)
{
   while (us-- > 0) {
      volatile int x=597;
      while (x-- > 0)
         __asm("nop");
   }
}

void rcc_init(void)
{ 
  // Enable Clocks to:
  RCC->APB2ENR |= RCC_APB2ENR_IOPCEN; //GPIOC
  RCC->APB2ENR |= RCC_APB2ENR_IOPAEN; //GPIOA
  RCC->APB2ENR |= RCC_APB2ENR_IOPBEN; //GPIOB (TIM)
  RCC->APB1ENR |= RCC_APB1ENR_TIM3EN; //TIM3 (PB0)
  RCC->APB2ENR |= RCC_APB2ENR_AFIOEN; //Alternate Function
  RCC->APB2ENR |= RCC_APB2ENR_SPI1EN; //SPI1
}

void gpio_init(void)
{
  //Set GPIO Direction CR & Mode up
  GPIOC->CRH = CRH_MODE_OUT(DEBUGLED0);        // set PortC8 to be GPIO out
  GPIOC->CRH |= CRH_MODE_OUT(DEBUGLED1);       // set PortC9 to be GPIO out
  GPIOA->CRL = CRL_MODE_OUT(VPRG);             // set VPRG to be GPIO out
  GPIOA->CRL |= CRL_MODE_OUT(XLAT);            // set XLAT to be GPIO out
  GPIOA->CRL |= CRL_MODE_OUT(DCPRG);           // set DCPRG to be GPIO out
  GPIOA->CRL |= CRL_MODE_OUT(BLANK);           // set BLANK to be GPIO out
  //SET GPIOA 5,7 as outputs which are using alternate push pull (50MHz) (1011 = B)
  GPIOA->CRL |= CRL_MODE(0x0000000B,SPI1_SCK); // set SPI1_SCK
  GPIOA->CRL |= CRL_MODE(0x0000000B,SPI1_MOSI); // set SPI1_MOSI
  //SET GPIOA 6 as input pull up (1000 = 8)
  GPIOA->CRL |= CRL_MODE(0x00000008,SPI1_MISO); // set SPI1_MOSI
  //GSCK 0
  //GPIOB->CRL = (GPIOB->CRL & 0xFFFFFFF0) |CRL_MODE(0x0000000B,GSCK);      // set GPIOB GSCK TIM CLK
  GPIOB->CRL = CRL_MODE(0x0000000B,GSCK);      // set GPIOB GSCK TIM CLK
}

void gsck_init(int clk)
{
  TIM_TimeBaseInitTypeDef  TIM_TimeBaseStructure;
  TIM_OCInitTypeDef  TIM_OCInitStructure;
  uint16_t CCR1_Val = 333;
  uint16_t CCR2_Val = 249;
  uint16_t CCR3_Val = 166;
  uint16_t CCR4_Val = 83;
  uint16_t PrescalerValue = 0;
 /* ---------------------------------------------------------------------
    The TIM3 is running at 36 KHz: TIM3 Frequency = TIM3 counter clock/(ARR + 1)
                                                  = 24 MHz / 666 = 36 KHz
    TIM3 Channel1 duty cycle = (TIM3_CCR1/ TIM3_ARR)* 100 = 50%
    TIM3 Channel2 duty cycle = (TIM3_CCR2/ TIM3_ARR)* 100 = 37.5%
    TIM3 Channel3 duty cycle = (TIM3_CCR3/ TIM3_ARR)* 100 = 25%
    TIM3 Channel4 duty cycle = (TIM3_CCR4/ TIM3_ARR)* 100 = 12.5%
  ----------------------------------------------------------------------- */

  PrescalerValue = (uint16_t) (SystemCoreClock / 24000000) - 1;
  TIM_TimeBaseStructure.TIM_Period = 665;
  TIM_TimeBaseStructure.TIM_Prescaler = PrescalerValue;
  TIM_TimeBaseStructure.TIM_ClockDivision = 0;
  TIM_TimeBaseStructure.TIM_CounterMode = TIM_CounterMode_Up;
  TIM_TimeBaseInit(TIM3, &TIM_TimeBaseStructure);

  /* PWM1 Mode configuration: Channel3 */
  TIM_OCInitStructure.TIM_OCMode = TIM_OCMode_PWM1;
  TIM_OCInitStructure.TIM_OutputState = TIM_OutputState_Enable;
  TIM_OCInitStructure.TIM_Pulse = CCR1_Val;
  TIM_OCInitStructure.TIM_OCPolarity = TIM_OCPolarity_High;
  TIM_OC3Init(TIM3, &TIM_OCInitStructure);
  TIM_OC3PreloadConfig(TIM3, TIM_OCPreload_Enable);

  /* TIM3 enable counter */
  TIM_Cmd(TIM3, ENABLE);
}

void tlc5940_init(void)
{
  //Init TLC5940 LED Driver Interface
  OUT_OFF(GPIOA,VPRG)
  OUT_OFF(GPIOA,XLAT)
  OUT_OFF(GPIOA,DCPRG)
  OUT_ON(GPIOA,BLANK)
  us_delay(1);
  OUT_OFF(GPIOA,BLANK)
  us_delay(1);
  //GSCK 0
  gsck_init(0);
}

void fb_init(void)
{
 int i,j;
 for(i = 0; i<4; i++)
   for(j = 0; j<24; j++)
     framebuff[i][j] = 0x00;
 }

void set_pixel(uint8_t x, uint8_t y, uint8_t r, uint8_t g, uint8_t b)
{
//Algorithm/*{{{*/
/*
Use Offset of 6 bytes which are currently unused

0: 0,1,2,3           RR GH GH BB
1: 4,5,6,7,8         HR HR GG HB HB
2: 9,10,11,12        RR GH GH BB
3: 13,14,15,16,17    HR HR GG HB HB
4: 18,19,20,21       RR GH GH BB
5: 22,23,24,25,26
6: 27,28,29,30

x=n even start=((n<<2)+(n>>1)) 
               start= red
               start+1 = green>>4
               start+2 = green<<4
               start+3 = blue

x=n odd start = ((n<<2)+((n-1)>>1))
              start = red>>4
              start+1 = red<<4
              start+2 = green
              start+3 = blue>>4
              start+4 = blue<<4
*//*}}}*/
  //r = b
  //g = r
  //b = g
  uint8_t starti = 0;
  x = 3-x;
  if(x & 0x01) //Odd x
  {
    starti = ((x<<2)+((x-1)>>1))+6;
    framebuff[y][starti] = b>>4;
    framebuff[y][starti+1] = b<<4;
    framebuff[y][starti+2] = r;
    framebuff[y][starti+3] = g>>4;
    framebuff[y][starti+4] = g<<4;
  }
  else //even x
  {
    starti = ((x<<2)+(x>>1))+6; 
    framebuff[y][starti] = b;
    framebuff[y][starti+1] = r>>4;
    framebuff[y][starti+2] = r<<4;
    framebuff[y][starti+3] = g;
  }
}

void write_row(void)
{
  //Choose Row
  //TODO
  OUT_ON(GPIOA,BLANK);
  OUT_OFF(GPIOA,BLANK);
  spiReadWrite(SPI1,0,framebuff[0], sizeof(framebuff[0]),SPI_FAST);
  //us_delay(1);
  OUT_ON(GPIOA,XLAT);
  OUT_OFF(GPIOA,XLAT);
}

int main(void)
{
    rcc_init();
    gpio_init();
    fb_init();
    spiInit(SPI1);
    ms_delay(5);
    tlc5940_init();
    //ms_delay(1);
    //set_pixel(0,0,0x00,0xFF,0x00);
    uint8_t i,j;
    for(;;)
    {
      for(i = 0; i< 0x3F; i++)
      {
        ms_delay(10);
        set_pixel(0,0,i,0x00,0x00);
        set_pixel(1,0,0x00,i,0x00);
        set_pixel(2,0,0x00,0x00,i);
        set_pixel(3,0,i,i,i);
        write_row();
      }
      for(j = 0x3F; i > 0; i--)
      {
        ms_delay(10);
        set_pixel(0,0,i,0x00,0x00);
        set_pixel(1,0,0x00,i,0x00);
        set_pixel(2,0,0x00,0x00,i);
        set_pixel(3,0,i,i,i);
        write_row();
      }
    }
}
