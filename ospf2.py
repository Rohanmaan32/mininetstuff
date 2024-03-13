from mininet.net import Mininet
from mininet.node import RemoteController, UserSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel

def create_network(num_nodes=50):
    # Create Mininet instance
    net = Mininet(controller=RemoteController, switch=UserSwitch)
    
    # Add remote controller (Floodlight)
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6653)
    
    # Add switches and hosts
    switches = []
    hosts = []
    for i in range(num_nodes):
        switch = net.addSwitch(f's{i+1}')
        switches.append(switch)
        host = net.addHost(f'h{i+1}')
        hosts.append(host)
        net.addLink(host, switch)
    
    # Connect switches in a linear topology
    for i in range(num_nodes - 1):
        net.addLink(switches[i], switches[i + 1])
    
    # Start network
    net.build()
    c0.start()
    for switch in switches:
        switch.start([c0])
    
    # Configure OSPF on each node
    for i in range(num_nodes):
        node = net.get(f's{i+1}')
        node.cmd('sudo service quagga start')
        node.cmd(f'vtysh -c "configure terminal" -c "router ospf" -c "network 10.0.{i+1}.0/24 area 0" -c "exit" -c "exit"')
    
    # Start CLI for user interaction
    CLI(net)
    
    # Clean up
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_network()
