# centos7kvm
This is some simple scripts used to deploy vm's on KVM

For host setup, refer to the following:

First, install the necessary packages. 
<code>yum -y install kvm virt-manager libvirt virt-install qemu-kvm xauth dejavu-lgc-sans-fonts bridge-utils policycoreutils-python</code>

Enable the kernel to do IP forwarding
<code>echo "net.ipv4.ip_forward = 1"|sudo tee /etc/sysctl.d/99-ipforward.conf</code>

Apply the new kernel settings
<code>sysctl -p /etc/sysctl.d/99-ipforward.conf</code>

Start libvirt and set it to start on boot
<code>systemctl start libvirtd 
systemctl enable libvirtd </code>

Create a network bridge for the VM's to share
<code>vi /etc/sysconfig/network-scripts/ifcfg-br0</code>

<blockquote>
DEVICE="br0"
ONBOOT="yes"
TYPE="Bridge"
BOOTPROTO="dhcp"
STP="on"
DELAY="0.0"
</blockquote>

Tell your network interface to be a slave to the bridge
<code>vi /etc/sysconfig/network-scripts/ifcfg-enp6s0f0 </code>

<blockquote>
DEVICE="enp3s0"
ONBOOT="yes"
BRIDGE="br0"
</blockquote>

Make sure to set your hostname
<code>vi /etc/hostname </code>

<blockquote>
hypervisor01.example.com
</blockquote>

Start networking to make sure the changes take effect
<code>systemctl restart network</code>

Make the directory to be your VM image folder
<code>mkdir /data</code>

Set the selinux policy on that new folder
<code>semanage fcontext -a -t virt_image_t "/data(/.*)?"</code>
<code>restorecon -R /data</code>

Tell libvirt you want to use the above folder for VMs
<code>virsh pool-destroy default</code>
<code>virsh pool-undefine default</code>
<code>virsh pool-define-as --name default --type dir --target /data</code>
<code>virsh pool-autostart default</code>
<code>virsh pool-build default</code>
<code>virsh pool-start default</code>
