# Makefile for Kalico generic_arduino simavr runner
#
# Builds a custom simavr runner that loads the firmware .elf
# and exposes UART0/UART1 via PTY.
#
# Requirements:
#   - simavr installed to $(SIMAVR_HOME)
#   - GCC, make
#
# Usage:
#   make                          Build runner
#   make run FIRMWARE=../.pio/build/mega2560/firmware.elf
#   make clean

SIMAVR_HOME ?= /home/${USER}/simavr
SIMAVR_DIR  := $(SIMAVR_HOME)/simavr
PARTS_DIR   := $(SIMAVR_HOME)/examples/parts

CC       := gcc
CFLAGS   := -O2 -g -Wall -Wextra
CPPFLAGS := -I$(SIMAVR_DIR) -I$(SIMAVR_DIR)/sim -I$(PARTS_DIR)
LDFLAGS  := -L$(SIMAVR_DIR)/obj-x86_64-linux-gnu -L$(PARTS_DIR)/obj-x86_64-linux-gnu
LDLIBS   := -lsimavr -lsimavrparts -lelf -lpthread -lutil

TARGET   := simavr_runner
FIRMWARE ?= ../.pio/build/mega2560/firmware.elf

.PHONY: all run clean

all: $(TARGET)

$(TARGET): simavr_runner.c
	$(CC) $(CFLAGS) $(CPPFLAGS) -o $@ $< $(LDFLAGS) $(LDLIBS)

run: $(TARGET)
	@echo "Starting simavr with firmware: $(FIRMWARE)"
	LD_LIBRARY_PATH=$(SIMAVR_DIR)/obj-x86_64-linux-gnu:$(PARTS_DIR)/obj-x86_64-linux-gnu \
	./$(TARGET) $(FIRMWARE)

clean:
	rm -f $(TARGET)

.PHONY: check
check:
	@echo "Checking simavr installation..."
	@test -f $(SIMAVR_DIR)/obj-x86_64-linux-gnu/libsimavr.so || { \
		echo "ERROR: simavr not built. Run: cd $(SIMAVR_HOME) && make RELEASE=0"; \
		exit 1; \
	}
	@echo "  simavr: OK"
	@test -f $(FIRMWARE) || { \
		echo "ERROR: Firmware not found. Run: cd .. && pio run -e mega2560"; \
		exit 1; \
	}
	@echo "  firmware: OK"
	@echo "All checks passed!"
