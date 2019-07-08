#!/usr/bin/env python
import os
import sys
import crypt
import argparse

def main():
    parser = argparse.ArgumentParser(description='Kickstart a Ubuntu 18.04 KVM')
    parser.add_argument("-n", "--name", 
                      dest="name", 
                      help="VM Name",
                      required=True)
    parser.add_argument("-c", "--cpu",
                      dest="cpu",
                      default="1",
                      help="How many vCPUs,")
    parser.add_argument("-r", "--ram",
                      dest="ram",
                      default="1024",
                      help="How much ram do you need,")
    parser.add_argument("-d", "--disk",
                      dest="size",
                      default="10",
                      help="How much disk space in gigs")
    parser.add_argument("-p", "--pass",
                      dest="pass",
                      default="password",
                      help="Root password")
    parser.add_argument("-u", "--user",
                      dest="user",
                      default=False,
                      help="User besides root to add and will have the same password as root",
                      required=True)
    try:
        options = parser.parse_args()
    except:
        if len(sys.argv) == 1:
            parser.print_help()
        return

    options = vars(options)
    hostname = options['name']
    passwd = options['pass']
    passwd_hash = crypt.crypt(passwd , crypt.mksalt(crypt.METHOD_SHA512))
    user = options['user']
    ram = options['ram']
    size = options['size']
    cpus = options['cpu']

    kickstart_file_content = """
#
#Kickstart template for Ubuntu
#Platform: x86-64
#
# Customized for Server 18.04 minimal vm install
#
# See README.mkd for usage

# Load the minimal server preseed off cdrom
preseed preseed/file string /cdrom/preseed/ubuntu-server-minimalvm.seed

# OPTIONAL: Change hostname from default 'preseed'
# If your DHCP hands out a hostname that will take precedence over this
# see: https://bugs.launchpad.net/ubuntu/+source/preseed/+bug/1452202
preseed netcfg/hostname string {}

# Use local proxy
# Setup a server with apt-cacher-ng and enter that hostname here
#preseed mirror/http/proxy string http://my-local-cache:3142/

#System language
lang en_US

#Language modules to install
langsupport en_US

#System keyboard
keyboard us

#System mouse
mouse

#System timezone
timezone --utc America/New_York

#Root password
rootpw --iscrypted {}

#Initial user (user with sudo capabilities)
user {} --fullname="{}" --password={} --iscrypted

#Reboot after installation
reboot

#Use text mode install
text

#Install OS instead of upgrade
install

#Installation media
url --url=http://archive.ubuntu.com/ubuntu/

#Change console size to 1024x768x24
# use set gfxpayload=1024x768x24,1024x768 before linux
# preseed debian-installer/add-kernel-opts string "vga=792"

#System bootloader configuration
bootloader --location=mbr

#Clear the Master Boot Record
zerombr yes

#Partition clearing information
clearpart --initlabel --drives vda
preseed partman-auto/disk string /dev/vda
preseed partman-auto-lvm/guided_size string 8192MB
part /boot --fstype=ext4 --size=1024 --asprimary
part pv.1 --grow --size=1 --asprimary
volgroup vg0 pv.1
logvol / --fstype=ext4 --name=root --vgname=vg0 --size=1 --grow
logvol swap --name=swap --vgname=vg0 --size=2048 --maxsize=2048



# Don't install recommended items by default
# This will also be set for built system at
# /etc/apt/apt.conf.d/00InstallRecommends
preseed base-installer/install-recommends boolean false

#System authorization infomation
auth --enableshadow

#Network information
network --bootproto=dhcp --device=auto

#Firewall configuration
# Not supported by ubuntu
# firewall --enabled --ssh

# Policy for applying updates. May be "none" (no automatic updates),
# "unattended-upgrades" (install security updates automatically), or
# "landscape" (manage system with Landscape).
# preseed pkgsel/update-policy select unattended-upgrades

#Do not configure the X Window System
skipx

%packages
# -- required for %post --
vim
software-properties-common
gpg-agent  # apt-key needs this when piping certs in through stdin
curl
openssh-server
net-tools  # this includes commands like ifconfig and netstat
wget
man


%post
# Set some defaults for apt to keep things tidy
cat > /etc/apt/apt.conf.d/90local <<"_EOF_"
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::AutocleanInterval "1";
APT::Periodic::MaxSize "200";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
#Acquire::http::Proxy "http://my-local-cache:3142";
_EOF_

# -- begin vim package customizations --
echo "set background=dark" >>/etc/vim/vimrc.local
# -- end vim package customizations --

# -- begin install git from 'Ubuntu Git Maintainers' PPA --
apt-get -qq -y update
apt-get -qq -y install git
# -- end install git from 'Ubuntu Git Maintainers' PPA --

# Clean up
apt-get -qq -y autoremove
apt-get clean
rm -f /var/cache/apt/*cache.bin
rm -rf /var/lib/apt/lists/*
    """.format(hostname, passwd_hash, user, passwd_hash, user)

    with open('/data/centos7kvm/tmp.ks', 'w') as f:
        f.write(kickstart_file_content)
    kickstartfile = "tmp.ks"
    
    virt_command = """virt-install --name {} --ram {} --disk """ + \
        """path=/data/images/{}.img,size={} --vcpus {} --os-type linux """ + \
        """--os-variant ubuntu18.04 --network bridge=br0 --graphics none """ + \
        """--console pty,target_type=serial --location """ + \
        """'http://archive.ubuntu.com/ubuntu/dists/bionic/main/installer-amd64/' """ + \
        """--initrd-inject=/data/centos7kvm/{} --extra-args """ + \
        """'ks=file:/{} console=ttyS0,115200n8 serial'"""

    os.system(virt_command.format(hostname, ram, hostname, size, cpus, kickstartfile, kickstartfile))

if __name__ == '__main__':
    main()

