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
### Localization
d-i debian-installer/locale string en_US
d-i console-setup/ask_detect boolean false
d-i keyboard-configuration/layoutcode string us

### Network configuration
d-i netcfg/choose_interface select auto
d-i netcfg/get_hostname string {}
d-i netcfg/get_domain string pingnattack.com
d-i netcfg/wireless_wep string

### Mirror settings
d-i mirror/http/countries select US
d-i mirror/country string US
d-i mirror/http/hostname string us.archive.ubuntu.com
d-i mirror/http/directory string /images/Ubuntu/18.04
d-i mirror/http/mirror select us.archive.ubuntu.com
d-i mirror/http/proxy string

### Clock and time zone setup
d-i clock-setup/utc boolean true
d-i time/zone string US/Eastern
d-i clock-setup/ntp boolean true

### Partitioning
d-i partman-auto/disk string /dev/vda
d-i partman-auto/method string lvm
d-i partman-lvm/device_remove_lvm boolean true
d-i partman-md/device_remove_md boolean true
d-i partman-lvm/confirm boolean true
d-i partman-lvm/confirm_nooverwrite boolean true
d-i partman-auto-lvm/guided_size string max
d-i partman-auto/choose_recipe select atomic
d-i partman/default_filesystem string ext4
d-i partman-partitioning/confirm_write_new_label boolean true
d-i partman/choose_partition select finish
d-i partman/confirm boolean true
d-i partman/confirm_nooverwrite boolean true

### Account setup
d-i passwd/root-login boolean false
d-i passwd/user-fullname string {}
d-i passwd/username string {}
d-i passwd/user-password-crypted password {}
d-i user-setup/encrypt-home boolean false

### Apt setup

### Package selection
tasksel tasksel/first multiselect
# Individual additional packages to install
d-i pkgsel/include string git openssh-server python-simplejson sudo
d-i pkgsel/update-policy select none
d-i pkgsel/upgrade select none
popularity-contest popularity-contest/participate boolean false

### Boot loader installation
d-i grub-installer/only_debian boolean true
d-i grub-installer/with_other_os boolean true

### Finishing up the installation
d-i finish-install/reboot_in_progress note
d-i debian-installer/exit/poweroff boolean true

### Preseeding other packages

#### Advanced options
d-i preseed/late_command string \
echo "{}    ALL=(ALL) NOPASSWD:ALL" >> /target/etc/sudoers; \
in-target ln -s /lib/systemd/system/serial-getty@.service /etc/systemd/system/getty.target.wants/serial-getty@ttyS0.service; \
rm -f /target/etc/ssh/ssh_host_*; \
in-target sed -i -e 's|exit 0||' /etc/rc.local; \
in-target sed -i -e 's|.*test -f /etc/ssh/ssh_host_dsa_key.*||' /etc/rc.local; \
in-target bash -c 'echo "test -f /etc/ssh/ssh_host_dsa_key || dpkg-reconfigure openssh-server" >> /etc/rc.local'; \
in-target bash -c 'echo "exit 0" >> /etc/rc.local'; \
echo "{}" > /target/etc/hostname; \ rm -rf /etc/resolv.conf ; \
echo "search pingnattack.com" > /etc/resolv.conf ; \
echo "nameserver 10.20.254.1" >> /etc/resolv.conf; \
    """.format(hostname, user, user, passwd_hash, user, hostname)

    with open('/data/centos7kvm/tmp.preseed', 'w') as f:
        f.write(kickstart_file_content)
    kickstartfile = "tmp.preseed"
    
    virt_command = """virt-install --name {} --ram {} --disk """ + \
        """path=/data/images/{}.img,size={} --vcpus {} --os-type linux """ + \
        """--os-variant ubuntu18.04 --network bridge=br0 --graphics none """ + \
        """--console pty,target_type=serial --location """ + \
        """'http://archive.ubuntu.com/ubuntu/dists/bionic/main/installer-amd64/' """ + \
        """--initrd-inject=/data/centos7kvm/{} --extra-args """ + \
        """'ks=file:/{} url=file:///{} console=tty0 console=ttyS0,115200n8 serial locale=en_US auto=true priority=critical netcfg/use_autoconfig=true netcfg/disable_dhcp=false netcfg/get_hostname={} netcfg/get_domain=pingnattack.com network-console/password=instpass network-console/start=true'"""

    os.system(virt_command.format(hostname, ram, hostname, size, cpus, kickstartfile, kickstartfile, kickstartfile, hostname))

if __name__ == '__main__':
    main()


