#ifndef __CANBUS_H__
#define __CANBUS_H__

#include <stdint.h> // uint32_t
#include "autoconf.h" // CONFIG_CANBUS_FD

struct canbus_msg {
    uint32_t id;
    uint32_t dlc;
    union {
        uint8_t data[64];
        uint32_t data32[16];
    };
};

#define CANMSG_ID_RTR (1<<30)
#define CANMSG_ID_EFF (1<<31)

// Convert data length to CAN FD DLC value (0-15)
static inline uint32_t
canbus_len_to_dlc(uint32_t len)
{
    if (len <= 8)
        return len;
    if (len <= 12)
        return 9;
    if (len <= 16)
        return 10;
    if (len <= 20)
        return 11;
    if (len <= 24)
        return 12;
    if (len <= 32)
        return 13;
    if (len <= 48)
        return 14;
    return 15;
}

// Convert CAN FD DLC value (0-15) to actual data length in bytes
static inline uint32_t
canbus_dlc_to_len(uint32_t dlc)
{
    if (dlc <= 8)
        return dlc;
    if (dlc == 9)
        return 12;
    if (dlc == 10)
        return 16;
    if (dlc == 11)
        return 20;
    if (dlc == 12)
        return 24;
    if (dlc == 13)
        return 32;
    if (dlc == 14)
        return 48;
    return 64;
}

// CAN FD payload per frame (accounting for framing overhead)
// Classic CAN: 8 bytes per frame. CAN FD: up to 64 bytes per frame.
#define CANBUS_PAYLOAD_LEN (CONFIG_CANBUS_FD ? 64 : 8)

// Extract the number of data bytes from a CAN message dlc field.
// Works for both Classic CAN (max 8) and CAN FD (max 64).
#if CONFIG_CANBUS_FD
#define CANMSG_DATA_LEN(msg) canbus_dlc_to_len((msg)->dlc)
#else
#define CANMSG_DATA_LEN(msg) ((msg)->dlc > 8 ? 8 : (msg)->dlc)
#endif

struct canbus_status {
    uint32_t rx_error, tx_error, tx_retries;
    uint32_t bus_state;
};

enum {
    CANBUS_STATE_ACTIVE, CANBUS_STATE_WARN, CANBUS_STATE_PASSIVE,
    CANBUS_STATE_OFF,
};

// callbacks provided by board specific code
int canhw_send(struct canbus_msg *msg);
void canhw_set_filter(uint32_t id);
void canhw_get_status(struct canbus_status *status);

// canbus.c
int canbus_send(struct canbus_msg *msg);
void canbus_set_filter(uint32_t id);
void canbus_notify_tx(void);
void canbus_process_data(struct canbus_msg *msg);

#endif // canbus.h
