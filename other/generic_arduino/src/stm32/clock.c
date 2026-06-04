/**
 * stm32/clock.c - STM32H723 clock configuration (PLL1 for 528MHz)
 *
 * Derived from Klipper src/stm32/stm32h7.c
 * Uses HSI (64MHz internal oscillator) as clock source.
 *
 * Clock tree:
 *   HSI 64MHz → DIVM1(4) → 16MHz → PLL1 VCO(×33) = 528MHz
 *     → DIVP1(÷1) → SYSCLK = 528MHz
 *     → HPRE(÷2) → HCLK = 264MHz (CPU, AXI, SRAM)
 *     → D1PPRE(÷2) → APB3 = 132MHz
 *     → D2PPRE1(÷2) → APB1 = 132MHz (TIM2, USART3)
 *     → D2PPRE2(÷2) → APB2 = 132MHz (USART1)
 *     → D3PPRE(÷2) → APB4 = 132MHz
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include "autoconf.h"
#include "internal.h"

/* ---- Clock line lookup (maps peripheral base address to RCC bits) ------ */

struct cline
lookup_clock_line(uint32_t periph_base)
{
    /* STM32H7 domain mapping:
     * D3: GPIOx (AHB4) at D3_AHB1PERIPH_BASE
     * D1: DMA, FMC, etc. (AHB3) at D1_AHB1PERIPH_BASE
     * D2: Most peripherals (APB1/APB2/AHB1/AHB2)
     */
    if (periph_base >= D3_AHB1PERIPH_BASE) {
        /* GPIO, etc. on AHB4 */
        uint32_t bit = 1 << ((periph_base - D3_AHB1PERIPH_BASE) / 0x400);
        return (struct cline){.en=&RCC->AHB4ENR, .rst=&RCC->AHB4RSTR, .bit=bit};
    } else if (periph_base >= D3_APB1PERIPH_BASE) {
        uint32_t bit = 1 << ((periph_base - D3_APB1PERIPH_BASE) / 0x400);
        return (struct cline){.en=&RCC->APB4ENR, .rst=&RCC->APB4RSTR, .bit=bit};
    } else if (periph_base >= D1_AHB1PERIPH_BASE) {
        uint32_t bit = 1 << ((periph_base - D1_AHB1PERIPH_BASE) / 0x400);
        return (struct cline){.en=&RCC->AHB3ENR, .rst=&RCC->AHB3RSTR, .bit=bit};
    } else if (periph_base >= D1_APB1PERIPH_BASE) {
        uint32_t bit = 1 << ((periph_base - D1_APB1PERIPH_BASE) / 0x400);
        return (struct cline){.en=&RCC->APB3ENR, .rst=&RCC->APB3RSTR, .bit=bit};
    } else if (periph_base >= D2_AHB2PERIPH_BASE) {
        uint32_t bit = 1 << ((periph_base - D2_AHB2PERIPH_BASE) / 0x400);
        return (struct cline){.en=&RCC->AHB2ENR, .rst=&RCC->AHB2RSTR, .bit=bit};
    } else if (periph_base >= D2_AHB1PERIPH_BASE) {
        uint32_t bit = 1 << ((periph_base - D2_AHB1PERIPH_BASE) / 0x400);
        return (struct cline){.en=&RCC->AHB1ENR, .rst=&RCC->AHB1RSTR, .bit=bit};
    } else if (periph_base >= D2_APB2PERIPH_BASE) {
        uint32_t bit = 1 << ((periph_base - D2_APB2PERIPH_BASE) / 0x400);
        return (struct cline){.en=&RCC->APB2ENR, .rst=&RCC->APB2RSTR, .bit=bit};
    } else {
        /* D2_APB1 (split into low and high) */
        uint32_t offset = ((periph_base - D2_APB1PERIPH_BASE) / 0x400);
        if (offset < 32) {
            uint32_t bit = 1 << offset;
            return (struct cline){
                .en=&RCC->APB1LENR, .rst=&RCC->APB1LRSTR, .bit=bit};
        } else {
            uint32_t bit = 1 << (offset - 32);
            return (struct cline){
                .en=&RCC->APB1HENR, .rst=&RCC->APB1HRSTR, .bit=bit};
        }
    }
}

/* Return the peripheral clock frequency (APB1/APB2 = CONFIG_CLOCK_FREQ/4) */
uint32_t
get_pclock_frequency(uint32_t periph_base)
{
    return FREQ_PERIPH;
}

/* Enable a peripheral clock */
void
enable_pclock(uint32_t periph_base)
{
    struct cline cl = lookup_clock_line(periph_base);
    *cl.en |= cl.bit;
    /* Read back to ensure write takes effect (posted write barrier) */
    (void)*cl.en;
}

/* Enable a GPIO port's clock */
void
gpio_clock_enable(GPIO_TypeDef *regs)
{
    uint32_t pos = ((uint32_t)regs - D3_AHB1PERIPH_BASE) / 0x400;
    RCC->AHB4ENR |= (1 << pos);
    (void)RCC->AHB4ENR;  /* read back for sync */
}

/* ---- PLL1 clock setup for 528MHz --------------------------------------- */

void
stm32_clock_setup(void)
{
    /* Enable LDO regulator (required for VOS1) */
    PWR->CR3 = PWR_CR3_LDOEN;
    while (!(PWR->CSR1 & PWR_CSR1_ACTVOSRDY))
        ;

    /* Set VOS1 (required for >400MHz) */
    PWR->D3CR = (3 << PWR_D3CR_VOS_Pos);  /* VOS1 = bits [15:14] = 0b11 */
    while (!(PWR->D3CR & PWR_D3CR_VOSRDY))
        ;

    /* Configure PLL1 from HSI (64MHz internal oscillator):
     *   PLL input = HSI / DIVM1 = 64 / 4 = 16 MHz
     *   VCO = PLL input × (DIVN1+1) = 16 × 33 = 528 MHz
     *   PLL1P output = VCO / (DIVP1+1) = 528 / 1 = 528 MHz (SYSCLK)
     *   PLL1Q output = VCO / (DIVQ1+1) = 528 / 4 = 132 MHz
     */

    /* Select HSI as PLL source, set DIVM1 = 4 (divide by 4 → 16MHz) */
    RCC->PLLCKSELR = RCC_PLLCKSELR_PLLSRC_HSI
        | (4 << RCC_PLLCKSELR_DIVM1_Pos);

    /* PLL1 configuration: input range 4-8MHz, enable P and Q outputs */
    RCC->PLLCFGR = (2 << RCC_PLLCFGR_PLL1RGE_Pos)  /* 4-8MHz input range */
        | RCC_PLLCFGR_DIVP1EN
        | RCC_PLLCFGR_DIVQ1EN;

    /* PLL1 dividers: DIVN1=32 (×33), DIVQ1=3 (÷4), DIVP1=0 (÷2) */
    RCC->PLL1DIVR = (32 << RCC_PLL1DIVR_N1_Pos)
        | (3 << RCC_PLL1DIVR_Q1_Pos)
        | (0 << RCC_PLL1DIVR_P1_Pos);

    /* Enable instruction and data caches */
    SCB_EnableICache();
    SCB_EnableDCache();

    /* Flash latency: 3 wait states for 528MHz at 3.3V, WRHIGHFREQ=2 */
    FLASH->ACR = FLASH_ACR_LATENCY_3WS | (2 << FLASH_ACR_WRHIGHFREQ_Pos);

    /* Set HPRE = /2 (HCLK = 264MHz), APB prescalers = /2 (APBx = 132MHz) */
    RCC->D1CFGR = RCC_D1CFGR_HPRE_DIV2 | RCC_D1CFGR_D1PPRE_DIV2;
    RCC->D2CFGR = RCC_D2CFGR_D2PPRE1_DIV2 | RCC_D2CFGR_D2PPRE2_DIV2;
    RCC->D3CFGR = RCC_D3CFGR_D3PPRE_DIV2;

    /* Enable PLL1 and wait for lock */
    RCC->CR |= RCC_CR_PLL1ON;
    while (!(RCC->CR & RCC_CR_PLL1RDY))
        ;

    /* Switch SYSCLK to PLL1 */
    RCC->CFGR = RCC_CFGR_SW_PLL1;
    while ((RCC->CFGR & RCC_CFGR_SWS_Msk) != RCC_CFGR_SWS_PLL1)
        ;
}
