/**
 * stm32/startup_stm32h723.s - Startup code for STM32H723
 *
 * Minimal startup that:
 * 1. Provides the vector table in .vector_table section
 * 2. Copies .data from flash to RAM
 * 3. Zeros .bss
 * 4. Calls SystemInit() to configure clocks
 * 5. Sets SCB->VTOR to the actual vector table location
 * 6. Calls main()
 *
 * The vector table is placed at the very start of the firmware image,
 * which is where the bootloader jumps to.  The first word is the
 * initial stack pointer, the second word is the reset handler address.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

    .syntax unified
    .cpu cortex-m7
    .fpu fpv5-d16
    .thumb

/* ---- Vector table (placed in .vector_table section) ---- */
    .section .vector_table, "ax", %progbits
    .global __vector_table
    .type __vector_table, %object

__vector_table:
    .word _stack_end            /* 0x00: Initial stack pointer */
    .word Reset_Handler         /* 0x04: Reset handler */
    .word NMI_Handler           /* 0x08: NMI */
    .word HardFault_Handler     /* 0x0C: Hard fault */
    .word MemManage_Handler     /* 0x10: Memory management fault */
    .word BusFault_Handler      /* 0x14: Bus fault */
    .word UsageFault_Handler    /* 0x18: Usage fault */
    .word 0                     /* 0x1C: Reserved */
    .word 0                     /* 0x20: Reserved */
    .word 0                     /* 0x24: Reserved */
    .word 0                     /* 0x28: Reserved */
    .word SVC_Handler           /* 0x2C: SVCall */
    .word DebugMon_Handler      /* 0x30: Debug monitor */
    .word 0                     /* 0x34: Reserved */
    .word PendSV_Handler        /* 0x38: PendSV */
    .word SysTick_Handler       /* 0x3C: SysTick */
    /* External IRQs (fill with default handlers) */
    .rept 150
    .word Default_Handler
    .endr

    .size __vector_table, . - __vector_table

/* ---- Reset handler ---- */
    .section .text.Reset_Handler, "ax", %progbits
    .global Reset_Handler
    .type Reset_Handler, %function

Reset_Handler:
    /* Set stack pointer (in case bootloader didn't) */
    ldr sp, =_stack_end

    /* Copy .data from flash to RAM */
    ldr r0, =_data_start
    ldr r1, =_data_end
    ldr r2, =_data_flash
    b .Ldata_check
.Ldata_loop:
    ldr r3, [r2], #4
    str r3, [r0], #4
.Ldata_check:
    cmp r0, r1
    blt .Ldata_loop

    /* Zero .bss */
    ldr r0, =_bss_start
    ldr r1, =_bss_end
    movs r2, #0
    b .Lbss_check
.Lbss_loop:
    str r2, [r0], #4
.Lbss_check:
    cmp r0, r1
    blt .Lbss_loop

    /* Set VTOR to our vector table location.
     * The bootloader may have set VTOR to its own vector table.
     * We override it here so our interrupt handlers work correctly. */
    ldr r0, =__vector_table
    ldr r1, =0xE000ED08        /* SCB->VTOR address */
    str r0, [r1]
    dsb
    isb

    /* Call main() (which calls stm32_clock_setup() + sched_main()) */
    bl main

    /* If main returns, loop forever */
.Lhang:
    b .Lhang

    .size Reset_Handler, . - Reset_Handler

/* ---- Default handler for unused interrupts ---- */
    .section .text.Default_Handler, "ax", %progbits
    .global Default_Handler
    .type Default_Handler, %function
Default_Handler:
    b Default_Handler
    .size Default_Handler, . - Default_Handler

/* ---- Weak aliases for interrupt handlers ---- */
    .weak NMI_Handler
    .thumb_set NMI_Handler, Default_Handler
    .weak HardFault_Handler
    .thumb_set HardFault_Handler, Default_Handler
    .weak MemManage_Handler
    .thumb_set MemManage_Handler, Default_Handler
    .weak BusFault_Handler
    .thumb_set BusFault_Handler, Default_Handler
    .weak UsageFault_Handler
    .thumb_set UsageFault_Handler, Default_Handler
    .weak SVC_Handler
    .thumb_set SVC_Handler, Default_Handler
    .weak DebugMon_Handler
    .thumb_set DebugMon_Handler, Default_Handler
    .weak PendSV_Handler
    .thumb_set PendSV_Handler, Default_Handler
    .weak SysTick_Handler
    .thumb_set SysTick_Handler, Default_Handler
