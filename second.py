from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink
def create_topology(depth):
 net = Mininet(controller=Controller, switch=OVSSwitch, link=TCLink)
 net.addController('c0')
 switches = []
 hosts = []
 
 core_switch = net.addSwitch('s1')
 def add_switches_and_hosts(parent_switch, current_depth, max_depth):
 if current_depth == max_depth:
 return
 depth_suffix = chr(97 + current_depth)
 
 for i in range(1, 4):
 switch_name = f's{depth_suffix}{i}'
 switch = net.addSwitch(switch_name)
 net.addLink(parent_switch, switch)
 switches.append(switch)
 add_switches_and_hosts(switch, current_depth + 1, max_depth)
 for j in range(1, 11):
 host_name = f'h{depth_suffix}{j}'
 host = net.addHost(host_name)
 net.addLink(parent_switch, host)
 hosts.append(host)
 add_switches_and_hosts(core_switch, 1, depth)
 net.build()
 net.start()
 for switch in switches:
 switch.cmd('sudo ovs-vsctl set bridge', switch, 'protocols=OpenFlow13')
 switch.cmd('sudo ovs-vsctl set-fail-mode', switch, 'secure')
 switch.cmd('sudo service openvswitch-switch restart')
 for switch in switches:
 switch.cmd('sudo service olsrd restart')
 return net
if __name__ == '__main__':
 setLogLevel('info')
 topology_depth = 4
 net = create_topology(topology_depth)
 CLI(net)
 net.stop()
