# Makefile for host-native Kalico MCU build
#
# Compiles the Kalico MCU protocol layer as a native executable
# using POSIX sockets for serial communication.
#
# Usage:
#   make          Build native executable
#   make run      Build and run (auto-assign port)
#   make clean    Remove build artifacts
#
# Requirements:
#   - GCC or Clang (Linux/macOS/WSL)
#   - MinGW-w64 (Windows native)
#
# SPDX-License-Identifier: GPL-3.0-or-later

CC       ?= gcc
CFLAGS   ?= -O2 -g -Wall -Wextra
LDLIBS   ?=

# Platform detection
UNAME_S := $(shell uname -s 2>/dev/null || echo Windows)
ifeq ($(findstring MINGW,$(UNAME_S)),MINGW)
  PLATFORM := Windows
  LDLIBS  += -lws2_32
  EXE_EXT := .exe
else ifeq ($(UNAME_S),Windows)
  PLATFORM := Windows
  LDLIBS  += -lws2_32
  EXE_EXT := .exe
else
  PLATFORM := Unix
  LDLIBS  += -lpthread
  EXE_EXT :=
endif

# Directories
NATIVE_DIR  = .
SRC_DIR     = ../src
BUILD_DIR   = build
BINARY      = $(BUILD_DIR)/kalico_mcu$(EXE_EXT)

# Include paths
INCLUDES = -I$(NATIVE_DIR) -I$(SRC_DIR)

# Source files — Kalico core + native platform layer
SRC_FILES = \
    $(SRC_DIR)/sched.c \
    $(SRC_DIR)/command.c \
    $(SRC_DIR)/basecmd.c \
    $(SRC_DIR)/debugcmds.c \
    $(SRC_DIR)/compile_time_request.c \
    $(SRC_DIR)/ctr_run.c \
    $(SRC_DIR)/registrations.c \
    $(SRC_DIR)/stepper.c \
    $(SRC_DIR)/generic/serial_irq.c \
    $(SRC_DIR)/generic/timer_irq.c \
    $(SRC_DIR)/generic/crc16_ccitt.c

NATIVE_FILES = \
    $(NATIVE_DIR)/main.c \
    $(NATIVE_DIR)/serial_native.c \
    $(NATIVE_DIR)/timer_native.c \
    $(NATIVE_DIR)/irq.c \
    $(NATIVE_DIR)/misc_native.c

ALL_SRC = $(SRC_FILES) $(NATIVE_FILES)

# Object files
SRC_OBJS   = $(patsubst $(SRC_DIR)/%.c,$(BUILD_DIR)/src/%.o,$(SRC_FILES))
NATIVE_OBJS = $(patsubst $(NATIVE_DIR)/%.c,$(BUILD_DIR)/native/%.o,$(NATIVE_FILES))
ALL_OBJS   = $(SRC_OBJS) $(NATIVE_OBJS)

# Compiler flags
CFLAGS += $(INCLUDES)
CFLAGS += -DCONFIG_NATIVE_BUILD=1

# ---------------------------------------------------------------------------
# Targets
# ---------------------------------------------------------------------------

.PHONY: all run clean help

all: $(BINARY)
	@echo "Build complete: $(BINARY)"
	@echo "Run: $(BINARY) [--port PORT]"

run: $(BINARY)
	$(BINARY) --port 0

clean:
	rm -rf $(BUILD_DIR)

help:
	@echo "Kalico Native MCU Build"
	@echo "======================="
	@echo "  make          Build native executable"
	@echo "  make run      Build and run (auto-assign port)"
	@echo "  make clean    Remove build artifacts"
	@echo ""
	@echo "  Platform: $(PLATFORM)"
	@echo "  CC:       $(shell $(CC) --version 2>&1 | head -1)"

# ---------------------------------------------------------------------------
# Build rules
# ---------------------------------------------------------------------------

$(BINARY): $(ALL_OBJS)
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -o $@ $^ $(LDLIBS)

$(BUILD_DIR)/src/%.o: $(SRC_DIR)/%.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -c -o $@ $<

$(BUILD_DIR)/native/%.o: $(NATIVE_DIR)/%.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -c -o $@ $<
