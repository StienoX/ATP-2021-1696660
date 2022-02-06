
#############################################################################
#
# Project Makefile
#
# (c) Wouter van Ooijen (www.voti.nl) 2016
#
# This file is in the public domain.
# 
#############################################################################

# source files in this project (main.cpp is automatically assumed)
SOURCES := pascal.asm

# header files in this project
HEADERS :=

# other places to look for files for this project
SEARCH  := ../hwlib/library ../Catch2/single_include/catch2/

# generating the asm file using the python pascal compiler
pascal.asm: pascal.txt
	python ../pascal_compiler/main.py -i "pascal.txt" -o "pascal.asm"

# project-specific settings
TARGET ?= arduino_due

BMPTK := ../bmptk
HWLIB := ../hwlib
CATCH := ../Catch2

# include the bmptk makefile.inc
include ../hwlib/makefile.inc

#overriding recipe clean to add .asm files
clean:
	rm -f *.asm *.ld *.bin *.elf *.map *.hex *.o bmptk_calculated_size_stack.c bmptk_calculated_size_stack.o bmptk_fixed_size_stack.c bmptk_fixed_size_stack.o bmptk_dummy_size_stack.c bmptk_dummy_size_stack.o _cc_flags _cpp_flags _linker_flags _linker_libs
