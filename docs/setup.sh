sudo apt-get update
sudo apt-get upgrade
sudo apt-get install net-tools git arping

#sudo rm /etc/{initramfs/post-update.d/,kernel/{postinst.d/,postrm.d/}}z50-raspi-firmware
#sudo apt purge raspi-firmware

cd ~
mkdir linuxcnc
cd linuxcnc
mkdir configs
cd configs
git clone https://github.com/andyalexander/cnc-plasma.git

#cd cnc-plasma

mkdir ~/linuxcnc/nc_files

sudo cp setup/99-usb.rules /etc/udev/rules.d/99-usb.rules
sudo udevadm control --reload-rules

# Mesa config tool
echo 'deb [arch=amd64] https://gnipsel.com/mesact/apt-repo stable main' | sudo tee /etc/apt/sources.list.d/mesact.list
sudo curl --silent --show-error https://gnipsel.com/mesact/apt-repo/pgp-key.public -o /etc/apt/trusted.gpg.d/mesact.ascsudo curl --silent --show-error https://gnipsel.com/mesact/apt-repo/pgp-key.public -o /etc/apt/trusted.gpg.d/mesact.asc
sudo apt update
sudo apt install mesact ethtool

# Github
(type -p wget >/dev/null || (sudo apt update && sudo apt install wget -y)) \
	&& sudo mkdir -p -m 755 /etc/apt/keyrings \
	&& out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
	&& cat $out | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
	&& sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
	&& sudo mkdir -p -m 755 /etc/apt/sources.list.d \
	&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
	&& sudo apt update \
	&& sudo apt install gh -y
	&& gh auth login


# https://wiki.debian.org/Wine#Installation_on_Debian_Jessie_and_newer
sudo dpkg --add-architecture i386 && sudo apt update
sudo apt install \
      wine \
      wine32 \
      wine64 \
      libwine \
      libwine:i386 \
      fonts-wine \
	  winbind

# This is an intel network, disable IRQ coalescing - edit this file to reflect the correct NIC	  
# after, running sudo ethtool -c enp0s31f6 | grep rx-usecs -> should show `rx-usecs:0`
sudo ethtool -c enp0s31f6 | grep rx-usecs &&
sudo cp setup/disable-coalescing  /etc/network/if-up.d/disable-coalescing

# Claude code
curl -fsSL https://claude.ai/install.sh | bash &&
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc


# Dropbox
sudo apt install python3-gpg -y &&
wget -O /tmp/dropbox.deb "https://linux.dropbox.com/packages/debian/dropbox_2026.05.06_amd64.deb" &&
sudo dpkg -i /tmp/dropbox.deb ; sudo apt-get install -f -y

# VScode
sudo apt install wget gpg apt-transport-https -y &&
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | sudo tee /usr/share/keyrings/packages.microsoft.gpg > /dev/null &&
sudo sh -c 'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/packages.microsoft.gpg] \
  https://packages.microsoft.com/repos/code stable main" \
  > /etc/apt/sources.list.d/vscode.list' &&
sudo apt update && sudo apt install code -y

# Networking
# If there are problems run: `sudo arping -I enp0s31f6 10.10.10.10` to do a L2 check
#Make the config non-managed
sudo bash -c 'cat > /etc/NetworkManager/conf.d/mesa.conf << EOF
[keyfile]
unmanaged-devices=interface-name:enp0s31f6
EOF' &&
sudo systemctl restart NetworkManager &&
nmcli dev status &&
sudo arping -I enp0s31f6 10.10.10.10

# Disable firewall rules
sudo iptables -I INPUT -i enp0s31f6 -j ACCEPT &&
sudo iptables -I OUTPUT -o enp0s31f6 -j ACCEPT

# Disable suspend (second command re-enables)
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
#sudo systemctl unmask sleep.target suspend.target hibernate.target hybrid-sleep.target
