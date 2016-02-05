# centos7kvm
This is some simple scripts used to deploy vm's on KVM

For host setup, refer to the following:

First, install the necessary packages.<br />
<code>yum -y install kvm virt-manager libvirt virt-install qemu-kvm xauth dejavu-lgc-sans-fonts bridge-utils policycoreutils-python</code>

Enable the kernel to do IP forwarding<br />
<code>echo "net.ipv4.ip_forward = 1"|sudo tee /etc/sysctl.d/99-ipforward.conf</code>

Apply the new kernel settings<br />
<code>sysctl -p /etc/sysctl.d/99-ipforward.conf</code>

Start libvirt and set it to start on boot<br />
<code>systemctl start libvirtd <br />
systemctl enable libvirtd </code>

Create a network bridge for the VM's to share<br />
<code>vi /etc/sysconfig/network-scripts/ifcfg-br0</code>

<blockquote>
DEVICE="br0"<br />
ONBOOT="yes"<br />
TYPE="Bridge"<br />
BOOTPROTO="dhcp"<br />
STP="on"<br />
DELAY="0.0"<br />
</blockquote>

Tell your network interface to be a slave to the bridge<br />
<code>vi /etc/sysconfig/network-scripts/ifcfg-enp6s0f0 </code>

<blockquote>
DEVICE="enp3s0"<br />
ONBOOT="yes"<br />
BRIDGE="br0"<br />
</blockquote><br />

Make sure to set your hostname<br />
<code>vi /etc/hostname </code>

<blockquote>
hypervisor01.example.com
</blockquote>

Start networking to make sure the changes take effect<br />
<code>systemctl restart network</code>

Make the directory to be your VM image folder<br />
<code>mkdir /data</code>

Set the selinux policy on that new folder<br />
<code>semanage fcontext -a -t virt_image_t "/data(/.*)?"</code><br />
<code>restorecon -R /data</code>

Tell libvirt you want to use the above folder for VMs<br />
<code>virsh pool-destroy default</code><br />
<code>virsh pool-undefine default</code><br />
<code>virsh pool-define-as --name default --type dir --target /data</code><br />
<code>virsh pool-autostart default</code><br />
<code>virsh pool-build default</code><br />
<code>virsh pool-start default</code><br />
