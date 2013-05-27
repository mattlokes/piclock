#define USE_STDPERIPH_DRIVER
#include "stm32f10x.h"

int main(void)
{
volatile uint32_t	dly;

RCC->APB2ENR |= RCC_APB2ENR_IOPCEN;

GPIOC->CRH = 0x00000003;

while (1) {
for(dly = 0; dly < 500000; dly++);
GPIOC->BSRR = (1 << 8);
for(dly = 0; dly < 500000; dly++);
GPIOC->BRR = (1 << 8);
}
}

//Quick hack, approximately 1ms delay
/*void ms_delay(int ms)
{
   while (ms-- > 0) {
      volatile int x=5971;
      while (x-- > 0)
         __asm("nop");
   }
}



//Flash orange LED at about 1hz
int main(void)
{
    RCC->APB2ENR |= RCC_APB2ENR_IOPCEN;  // enable the clock to GPIOC
    GPIOC->CRH = GPIO_CRH_MODE8;        // set PortA to be general purpose output

    for (;;) {
       ms_delay(500);
       GPIOC->ODR ^= (1 << 8);           // Toggle the pin 
    }
}*/
