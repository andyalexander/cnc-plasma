# cnc-plasma



## USB devices

* Install `usbutils` to see the connected USB devices:
 - Run `sudo lsusb`, the device has the manufacturer 'Silicon Labs'
 - create a udev rule to assign a fixed name to the device in `/etc/udev/rules.d/99-usb.rules` which contains the following line:
 - to test the pendant,then run:
        * halrun 
        * loadusr xhc-whb04b-6 -uek

* https://linuxcnc.org/docs/2.8/html/man/man1/xhc-whb04b-6.1.html
* https://youtu.be/e2DjkzCq7R4


### THCAD
* https://jscalc.io/calc/NTr5QDX6WgMThBVb
* scale = thcad_model_voltage * frequency_divider * plasma_divider_ratio / (max_voltage_frequency - zero_voltage_frequency)
* offset = zero_voltage_frequency / frequency_divider
