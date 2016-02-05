#!/usr/bin/env python
import os
import sys
import crypt
from optparse import OptionParser

def main():
    parser = OptionParser(usage="usage: %prog [options] filename",
                          version="%prog 1.0")
    parser.add_option("-n", "--name",
                      action="store_true",
                      dest="name",
                      default=False,
                      help="VM Name")
    parser.add_option("-c", "--cpu",
                      action="store",
                      dest="cpu",
                      default="1",
                      help="How many vCPUs,",)
    parser.add_option("-r", "--ram",
                      action="store",
                      dest="ram",
                      default="1024",
                      help="How much ram do you need,",)
    parser.add_option("-d", "--disk",
                      action="store",
                      dest="size",
                      default="10",
                      help="How much disk space in gigs",)
    parser.add_option("-p", "--pass",
                      action="store",
                      dest="pass",
                      default="password",
                      help="Root password",)
    parser.add_option("-u", "--user",
                      action="store",
                      dest="user",
                      default=False,
                      help="User besides root to add and will have the same password as root",)
    (options, args) = parser.parse_args()

    if options.name is None:
        parser.error('Machine name not given')
        parser.print_help()
        sys.exit(1)

    if options.user is None:
        parser.error('Machine user not given')
        parser.print_help()
        sys.exit(1)

    if len(args) == 0:
        parser.print_help()
        sys.exit(1)

    options = vars(options)
    hostname = args[0]
    passwd = options['pass']
    passwd_hash = crypt.crypt(passwd , crypt.mksalt(crypt.METHOD_SHA512))
    user = options['user']
    ram = options['ram']
    size = options['size']
    cpus = options['cpu']

    kickstart_file_content = """
install
cmdline

#version=DEVEL
# System authorization information
auth --enableshadow --passalgo=sha512

# Use network installation
url --url="http://www.gtlib.gatech.edu/pub/centos/7/os/x86_64/"

# Use text mode install
text

# Run the Setup Agent on first boot
firstboot --enable

# use the whole disk
ignoredisk --only-use=vda

# Keyboard layouts
keyboard --vckeymap=us --xlayouts='us'

# System language
lang en_US.UTF-8

# repository
repo --name="CentOS Repo" --baseurl=http://www.gtlib.gatech.edu/pub/centos/7/os/x86_64/

# by specifying the update Repo the install process will automatically update to the latest version. 
# If you wish to stay at the initial release version, comment the following line.
repo --name="CentOS Repo Update" --baseurl=http://www.gtlib.gatech.edu/pub/centos/7/updates/x86_64/

# Network information
# dhcp
network  --bootproto=dhcp --device=eth0 --ipv6=auto --activate

# hostname
network  --hostname=%s

# firewall
firewall --enabled --ssh

# Root password
# to generate your own hash, run the following command
# python -c 'import crypt; print(crypt.crypt("passwordhere", crypt.mksalt(crypt.METHOD_SHA512)))'
rootpw --iscrypted %s

# add your own user
user --groups=wheel --name=%s --password=%s --iscrypted --gecos="%s"

# Do not configure the X Window System
skipx

# System timezone
timezone America/New_York --isUtc

# System bootloader configuration
bootloader --append=" crashkernel=auto" --location=mbr --boot-drive=vda

# thin partition
autopart --type=thinp

# Partition clearing information
clearpart --all --initlabel --drives=vda

# accept licensing
eula --agreed

# poweroff after install
poweroff

%%packages
@core
kexec-tools

%%end

%%addon com_redhat_kdump --enable --reserve-mb='auto'

%%end

%%post

# cleanup the installation
yum clean all

# create default ssh keys
ssh-keygen -q -t rsa -N "" -f /root/.ssh/id_rsa

# create default authorized_keys file
cp -p -f --context=system_u:object_r:ssh_home_t:s0 /root/.ssh/id_rsa.pub /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys

# run Aide to generate initial database
aide -i

# update
yum -y update

%%end
    """ % (hostname, passwd_hash, user, passwd_hash, user)

    with open('/data/centos7kvm/tmp.ks', 'w') as f:
        f.write(kickstart_file_content)
    kickstartfile = "tmp.ks"
    virt_command = """virt-install --name %s --ram %s --disk """ + \
        """path=/data/images/%s.img,size=%s --vcpus %s --os-type linux """ + \
        """--os-variant centos7.0 --network bridge=br0 --graphics none """ + \
        """--console pty,target_type=serial --location """ + \
        """'http://www.gtlib.gatech.edu/pub/centos/7/os/x86_64/' """ + \
        """--initrd-inject=/data/centos7kvm/%s --extra-args """ + \
        """'ks=file:/%s console=ttyS0,115200n8 serial'"""

    os.system(virt_command % (hostname, ram, hostname, size, cpus, kickstartfile, kickstartfile))

if __name__ == '__main__':
    main()
