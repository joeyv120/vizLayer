""" Visual indicator of active QMK layers

Author: Joe Vinciguerra
Date: 2020.08.21

This program provides a visual indication of the active layer on a
QMK-powered keyboard. A floating icon appears on top of other windows.
The program monitors the active layer number through an HID interface,
and changes the icon with the layer.

For help with required modules:
https://github.com/rene-aguirre/pywinusb/blob/master/examples/raw_data.py
https://pysimplegui.readthedocs.io/en/latest/call%20reference/#systemtray
"""


from pywinusb import hid
from PySimpleGUI import SystemTray
import ctypes
hllDll = ctypes.WinDLL ("User32.dll")


def sample_handler(data):
    # print("Raw data: {0}".format(data))  # Print raw data for debug
    data = [item for item in data if item != 0]  # remove blank characters
    if data is None:
        icon = 'default.png'  # Use this if you can't find a match
    else:
        data = [chr(item) for item in data]  # Convert int to chr
        icon = ''.join(data) + '.png'
    tray.Update(filename=icon)  # Update the icon on the screen


def hid_devices():
    all_hids = hid.find_all_hid_devices()  # Get a list of HID objects
    if all_hids:
        # Convert to a dictionary of Names:Objects
        hids_dict = {}
        for device in all_hids:
            device_name = str("{0.vendor_name} {0.product_name}" \
                    "(vID=0x{1:04x}, pID=0x{2:04x})"\
                    "".format(device, device.vendor_id, device.product_id))
            hids_dict[device_name] = device
        return hids_dict
    return None


def hid_read(hids_dict, menu_item):
    device = hids_dict[menu_item]  # Match the selection to the HID object
    device.open()  # Open the HID device for communication
    device.set_raw_data_handler(sample_handler)  # Set raw data callback
    return device  # Return the HID device


def menu_update():
    hids_dict = hid_devices()  # Get a dictionary of HID devices
    device_names = list(hids_dict.keys())  # Pull the names to a list
    # Generate a menu list to pass to the icon
    menu_items = [
        'BLANK',
        [
            'Refresh',
            'Device List',
            device_names,
            '---',
            'E&xit'
        ]
    ]
    tray.update(menu=menu_items)  # Update the icon with the menu list
    return hids_dict


# https://stackoverflow.com/questions/21160100/python-3-x-getting-the-state-of-caps-lock-num-lock-scroll-lock-on-windows
# https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
# https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getkeystate
def check_locks():
    lock_keys = {
        'VK_CAPITAL': 0x14,
        'VK_NUMLOCK': 0x90,
        'VK_SCROLL': 0x91,
    }
    lock_states={k:hllDll.GetKeyState(v) for k,v in lock_keys.items()}
    print(lock_states)

if __name__ == "__main__":
    # Create the tray icon
    tray = SystemTray(
            menu=['BLANK', ['Refresh', '---', 'E&xit']],
            filename='default.png',
    )
    hids_dict = menu_update()  # Populate the menu with HID devices
    device = None
    while True:  # The event loop
        menu_item = tray.read(timeout=100)  # Read the systemtray events/values
        if menu_item == 'Exit':
            break
        elif menu_item == 'Refresh':
            hids_dict = menu_update()  # Refesh the list of HID devices
        elif menu_item in [None, '__ACTIVATED__']:
            continue  # If there was no interaction of consequence
        elif menu_item == '__TIMEOUT__':
            check_locks()
        else:
            # Otherwise assume a device was selected
            try:
                device.close()  # Try to close any open devices first
            except:
                pass
            finally:
                device = hid_read(hids_dict, menu_item)  # Open the device
    try:
        device.close()  # Try to close any open devices first
    except:
        pass