sudo apt-get update
sudo apt-get upgrade
sudo apt-get install net-tools
sudo apt-get install git

#sudo rm /etc/{initramfs/post-update.d/,kernel/{postinst.d/,postrm.d/}}z50-raspi-firmware
#sudo apt purge raspi-firmware

sudo cp ../setup/99-usb.rules /etc/udev/rules.d/99-usb.rules
sudo udevadm control --reload-rules