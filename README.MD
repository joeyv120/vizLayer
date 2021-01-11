# VizLayer for QMK

This program provides a visual indication of the active layer on a QMK-powered keyboard.

A floating icon appears on top of other windows. The program monitors the active layer number through an HID interface, and changes the icon with the layer.

![Demo Animation](demo.gif)

## Requirements
Intended for use with Windows 10. Written in Python 3.8, and uses the PySimpleGUI, and pywinusb modules.

Include the following code in your QMK keymap.c file, and re-flash your board.

```
#include <print.h>

uiint32_t layer_state_set_user(uint32_t state) {
    uint8_t layer = biton32(state);
    xprintf("%d", layer);
    return state;
}
```

## Usage

1. Downlaod and unzip VizLayer.zip
2. Run VizLayer.exe (some anti-virus programs will throw flags, so you may need to create an exeption)
3. Right-click on the icon and select the appropriate HID device.
4. Watch the icon change with the keyboard layers.

This compiled version currently supports 8 layers (0-7), and the icon names are hardcoded, but the icons can be changed, but the naming convention must be maintained. Icons are located in the /data folder.

## Notes on source code:

The program looks for a PNG file named for the active layer number. For example, a keyboard with 3 layers will require png files named 0.png, 1.png, and 2.png. There are 8 simple example icons provided. The "default.png" file is loaded at program start, prior to connecting to an HID device. All of these png files can be customized, as long as this file naming scheme is followed.

## Future Work
* Add indication of Caps lock and number lock states
* Add error handling, and detect communication errors.
