sudo apt-get update
sudo apt-get upgrade
sudo apt-get install net-tools
sudo apt-get install git

#sudo rm /etc/{initramfs/post-update.d/,kernel/{postinst.d/,postrm.d/}}z50-raspi-firmware
#sudo apt purge raspi-firmware

#cd ~
#mkdir linuxcnc
#cd linuxcnc
#mkdir configs
#cd configs
#git clone https://github.com/andyalexander/cnc-plasma.git

#cd cnc-plasma

mkdir ~/linuxcnc/nc_files

sudo cp setup/99-usb.rules /etc/udev/rules.d/99-usb.rules
sudo udevadm control --reload-rules

echo 'deb [arch=amd64] https://gnipsel.com/mesact/apt-repo stable main' | sudo tee /etc/apt/sources.list.d/mesact.list
sudo curl --silent --show-error https://gnipsel.com/mesact/apt-repo/pgp-key.public -o /etc/apt/trusted.gpg.d/mesact.asc
sudo apt update
sudo apt install mesact

(type -p wget >/dev/null || (sudo apt update && sudo apt install wget -y)) \
	&& sudo mkdir -p -m 755 /etc/apt/keyrings \
	&& out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
	&& cat $out | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
	&& sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
	&& sudo mkdir -p -m 755 /etc/apt/sources.list.d \
	&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
	&& sudo apt update \
	&& sudo apt install gh -y