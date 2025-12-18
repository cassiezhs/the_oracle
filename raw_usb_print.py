import usb.core
import usb.util
import time

# ======================
# CONFIGURATION
# ======================
# Replace these with your printer's IDs if needed
VENDOR_ID = 0x6868   # placeholder
PRODUCT_ID = 0x0200  # placeholder
INTERFACE = 0

# ======================
# FIND USB DEVICE
# ======================
dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
if dev is None:
    raise RuntimeError("USB printer not found")

claimed = False

try:
    # Try to use the current configuration.
    # Only set it if none is active.
    try:
        dev.get_active_configuration()
    except usb.core.USBError:
        dev.set_configuration()

    cfg = dev.get_active_configuration()
    intf = cfg[(INTERFACE, 0)]

    # Detach kernel driver if it is currently attached
    if dev.is_kernel_driver_active(INTERFACE):
        dev.detach_kernel_driver(INTERFACE)

    # Claim the USB interface explicitly
    usb.util.claim_interface(dev, INTERFACE)
    claimed = True

    # Locate the bulk OUT endpoint
    ep_out = usb.util.find_descriptor(
        intf,
        custom_match=lambda e:
            usb.util.endpoint_direction(e.bEndpointAddress)
            == usb.util.ENDPOINT_OUT
    )

    if ep_out is None:
        raise RuntimeError("OUT endpoint not found")

    # ======================
    # ESC/POS COMMANDS
    # ======================
    INIT = b"\x1b@"  # Initialize printer
    TEXT = b"The oracle is awake.\nYour path is unfolding.\n\n"
    CUT  = b"\x1dVA0"  # Full cut

    # Send data in small chunks for stability
    for chunk in (INIT, TEXT, CUT):
        ep_out.write(chunk)
        time.sleep(0.05)

    print("Sent to printer.")

finally:
    # Release the interface only if it was successfully claimed
    if claimed:
        try:
            usb.util.release_interface(dev, INTERFACE)
        except usb.core.USBError:
            pass

    usb.util.dispose_resources(dev)
