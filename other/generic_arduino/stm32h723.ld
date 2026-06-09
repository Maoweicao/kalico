/*
 * STM32H723 Linker Script for generic_arduino
 *
 * Configurable flash origin for bootloader compatibility.
 * Build with: make -f Makefile.stm32 FLASH_ORIGIN=0x08002000
 *   or:        make -f Makefile.stm32 (defaults to 0x08000000)
 *
 * The FLASH_ORIGIN symbol is passed via --defsym at link time.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

OUTPUT_FORMAT("elf32-littlearm", "elf32-littlearm", "elf32-littlearm")
OUTPUT_ARCH(arm)

_rom_origin = DEFINED(FLASH_ORIGIN) ? FLASH_ORIGIN : 0x08000000;

MEMORY
{
    rom  (rx)  : ORIGIN = _rom_origin, LENGTH = 256K
    ram  (rwx) : ORIGIN = 0x20000000,  LENGTH = 128K
}

SECTIONS
{
    .text : {
        . = ALIGN(4);
        _text_vectortable_start = .;
        KEEP(*(.vector_table))
        _text_vectortable_end = .;
        *(.text .text.*)
        *(.rodata .rodata*)
    } > rom

    /* ARM exception tables (needed for C++ unwinding and libgcc) */
    __exidx_start = .;
    .ARM.exidx : {
        *(.ARM.exidx* .gnu.linkonce.armexidx.*)
    } > rom
    __exidx_end = .;

    .ARM.extab : {
        *(.ARM.extab* .gnu.linkonce.armextab.*)
    } > rom

    . = ALIGN(4);
    _data_flash = .;

    .data : AT (_data_flash)
    {
        . = ALIGN(4);
        _data_start = .;
        *(.ramfunc .ramfunc.*);
        *(.data .data.*);
        . = ALIGN(4);
        _data_end = .;
    } > ram

    .bss (NOLOAD) :
    {
        . = ALIGN(4);
        _bss_start = .;
        *(.bss .bss.*)
        *(COMMON)
        . = ALIGN(4);
        _bss_end = .;
    } > ram

    _stack_start = 0x20000000 + 128K - 512 - 8;
    .stack _stack_start (NOLOAD) :
    {
        . = . + 512;
        _stack_end = .;
    } > ram

    /DISCARD/ : {
        *(.init)
        *(.fini)
    }
}
