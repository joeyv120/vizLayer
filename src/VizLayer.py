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

To do:
    * Implement bluetooth: try this one: https://github.com/tmcneal/bluefang
    * Default icon when the source changes, or the refresh button is pressed

"""


from pywinusb import hid
from PySimpleGUI import SystemTray
import ctypes
hllDll = ctypes.WinDLL("User32.dll")


def sample_handler(data):
    # print("\nRaw data: {0}".format(data))  # Print raw data for debug
    data = [item for item in data if item != 0]  # remove blank characters
    # print(data)
    data = [chr(item) for item in data]  # Convert int to chr
    # print(data)
    icon = 'data\\' + ''.join(data[-1]) + '.png'  # read the last if multiple
    # try:
    tray_layers.Update(filename=icon)  # Update the icon on the screen
    # except:
    # tray_layers.Update(filename='data\\default.png')  # Use this on error


def hid_devices():
    all_hids = hid.find_all_hid_devices()  # Get a list of HID objects
    # Convert to a dictionary of Names:Objects
    hids_dict = {}
    for device in all_hids:
        device_name = str(
                "{0.vendor_name} {0.product_name}"
                "(vID=0x{1:04x}, pID=0x{2:04x})"
                "".format(device, device.vendor_id, device.product_id)
        )
        hids_dict[device_name] = device
    return hids_dict


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
    tray_layers.update(menu=menu_items)  # Update the icon with the menu list
    return hids_dict


# https://stackoverflow.com/questions/21160100/python-3-x-getting-the-state-of-caps-lock-num-lock-scroll-lock-on-windows
# https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
# https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getkeystate
def check_locks():
    lock_keys = {
        'CAP': 0x14,
        'NUM': 0x90,
        # 'VK_SCROLL': 0x91,
    }
    lock_states = {k: hllDll.GetKeyState(v) for k, v in lock_keys.items()}
    return lock_states


def change_locks(lock_states):
    message = ''
    if lock_states['CAP'] == 1:
        message += 'Caps Lock = ON'
    else:
        message += 'Caps Lock = OFF'
    if lock_states['NUM'] == 1:
        message += '\nNum Lock = ON'
    else:
        message += '\nNum Lock = OFF'
    tray_layers.ShowMessage(
        title='Lock States',
        message=message,
        time=(10, 1000),
        filename='data\\locks.png',
    )
    print(lock_states)
    return


if __name__ == "__main__":
    # Create the tray icon for layers
    tray_layers = SystemTray(
            menu=['BLANK', ['Refresh', '---', 'E&xit']],
            filename='data\\default.png',
    )
    # Create the tray icon for locks
    # tray_locks = SystemTray(
    #         # menu=['BLANK', ['Refresh', '---', 'E&xit']],
    #         filename='data\\default.png',
    # )
    # tray_locks.hide()

    hids_dict = menu_update()  # Populate the menu with HID devices
    device = None
    lock_states_old = None
    while True:  # The event loop
        menu_item = tray_layers.read(timeout=100)  # Read the systemtray
        if menu_item == 'Exit':
            break
        elif menu_item == 'Refresh':
            hids_dict = menu_update()  # Refesh the list of HID devices
        elif menu_item in [
                    None,
                    '__ACTIVATED__',
                    '__MESSAGE_CLICKED__',
                    '__DOUBLE_CLICKED__',
                    ]:
            continue  # If there was no interaction of consequence
        elif menu_item == '__TIMEOUT__':
            lock_states_new = check_locks()
            if lock_states_new != lock_states_old:
                change_locks(lock_states_new)
            lock_states_old = lock_states_new
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
