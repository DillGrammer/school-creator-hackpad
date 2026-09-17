import usb_cdc, usb_hid
usb_cdc.enable(console=False, data=True)
# All actions are dispatched once by the helper; no duplicate HID key injection.
usb_hid.disable()
