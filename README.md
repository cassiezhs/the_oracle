**The Oracle** is a small physical computing project built on a Raspberry Pi that generates short oracle texts using OpenAI and prints them directly to paper via a USB thermal receipt printer.

The system communicates with the printer at the USB device level using raw ESC/POS commands, treating printed paper as the sole output interface. There is no system print queue, no display, and no stored state. Once a message is printed and cut, the interaction is complete.

This repository focuses on reproducible setup, minimal working scripts, and direct USB printing from Python.

---

## Features

- Local web interface for submitting oracle topics
- Text generation using OpenAI
- Direct USB communication with a thermal printer (ESC/POS)
- No CUPS or system print drivers
- Stateless, single-interaction execution model
- Printer-compatible text encoding (no UTF-8 corruption)

---

## Hardware Requirements

- Raspberry Pi (any model with USB support)
- USB thermal receipt printer (ESC/POS compatible)
- Dedicated power supply for the printer

---

## System Dependencies

USB access requires `libusb`.

```bash
sudo apt install libusb-1.0-0 libusb-1.0-0-dev
