## LinuxCNC

### Installation
* Post install, do an `sudo apt-get update` then `sudo apt-get upgrade`
* If you see an error about raspi firmware then run:
  * `sudo rm /etc/{initramfs/post-update.d/,kernel/{postinst.d/,postrm.d/}}z50-raspi-firmware`
  * `sudo apt purge raspi-firmware`
* To check the version you are running execuate `uname -r`
* 



## General hardware
* Make sure you disable secure boot in the bios
* MESA manual https://www.mesanet.com/pdf/parallel/7i95tman.pdf


### Latency

Taken from: https://forum.linuxcnc.org/27-driver-boards/52849-error-finishing-read


* Run `latency-histogram --nobase --sbinsize 1000`

* Disable all power management options in the BIOS setup. This include turbo modes, EIST, Cstates > C1, Cool&Quiet etc, basically anything that causes the CPU to change speeds dynamically or sleep.

* Also in the BIOS you should disable hyperthreading and any management engine  related  options that affect the network (like AMT)

* If your PC has an Intel Ethernet chip make sure you disable IRQ coalescing (man hm2_eth)

* Pinging the 7I96S will give you some idea of network latency
```
ping -i .2 -c 4 10.10.10.10
sudo chrt 99 ping -i .001 -q 10.10.10.10
```

 (let the last command run for a few minutes and
then stop it with a control C, it will print timing statistics)



## Debian config

* to install `ifconfig` run `sudo apt-get install net-tools`
* then run `/sbin/ifconfig` to check the network status
* run network setup, add a second ethernet adaptor with ip `10.10.10.1` no gateway


## Torch height controller

* Manual: https://www.mesanet.com/pdf/analog/thcad2man.pdf
* If you are using QTPlasmac - the offset and scale parameters are in the parameters screen in the UI, the ones in he HAL file don't matter
* If using ohmic probe, you must check `ohmic probe enable` in the GUI

## Ohmic sensor

https://linuxcnc.org/docs/2.9/html/plasma/plasma-cnc-primer.html#_initial_height_sensing


## QTPlasmac hints
* On the 'settings' page make sure that 'KB shortcuts' is enabled if you want to be able to use keyboard jogging
* 


## Useful links
* https://linuxcnc.org/docs/html/plasma/plasma-cnc-primer.html