from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
def create_topology():
 net = Mininet(controller=Controller, switch=OVSSwitch)
 net.addController('c0')
 # Add switches and hosts
 s1 = net.addSwitch('s1')
 h1 = net.addHost('h1')
 h2 = net.addHost('h2')
 net.addLink(s1, h1)
 net.addLink(s1, h2)
 # Install and configure Quagga on the switch
 s1.cmd('apt-get update')
 s1.cmd('apt-get install -y quagga')
 s1.cmd('cp /usr/share/doc/quagga/examples/zebra.conf.sample /etc/quagga/zebra.conf')
 s1.cmd('cp /usr/share/doc/quagga/examples/ospfd.conf.sample /etc/quagga/ospfd.conf')
 s1.cmd('chmod 644 /etc/quagga/*.conf')
 s1.cmd('service quagga restart')
 # Configure OSPF
 s1.cmd('sudo vtysh -c "configure terminal" -c "router ospf" -c "network 0.0.0.0/0 area 0" -c 
"end" -c "write"')
 net.start()
 return net
if __name__ == '__main__':
 setLogLevel('info')
 net = create_topology()
 CLI(net)
 net.stop()
