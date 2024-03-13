from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel

def create_network():
    # Create a Mininet instance
    net = Mininet(controller=Controller, switch=OVSSwitch)
    
    # Add controller
    c0 = net.addController('c0')
    
    # Add switch
    s1 = net.addSwitch('s1')
    
    # Add hosts
    h1 = net.addHost('h1')
    h2 = net.addHost('h2')
    
    # Add links
    net.addLink(h1, s1)
    net.addLink(h2, s1)
    
    # Start network
    net.build()
    c0.start()
    s1.start([c0])
    
    # Start CLI for user interaction
    CLI(net)
    
    # Clean up
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_network()
