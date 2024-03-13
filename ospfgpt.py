from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.node import RemoteController

def create_network(num_hosts=4):
    # Create a Mininet instance
    net = Mininet(controller=RemoteController, switch=OVSSwitch)
    
    # Add remote controller
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)
    
    # Add switches
    switches = {}
    for i in range(1, num_hosts+1):
        switch = net.addSwitch(f's{i}')
        switches[f's{i}'] = switch
    
    # Add hosts
    hosts = {}
    for i in range(1, num_hosts+1):
        host = net.addHost(f'h{i}')
        hosts[f'h{i}'] = host
    
    # Add links
    for i in range(1, num_hosts+1):
        net.addLink(hosts[f'h{i}'], switches[f's{i}'])
    
    # Start network
    net.build()
    c0.start()
    for switch in switches.values():
        switch.start([c0])
    
    # Start CLI for user interaction
    CLI(net)
    
    # Clean up
    net.stop()

def benchmark_network(net):
    # Run pingall to generate network traffic
    print("Running pingall to generate traffic...")
    result = net.pingAll()
    print("Pingall result:", result)
    
    # Measure bandwidth between h1 and h2
    h1, h2 = net.get('h1', 'h2')
    print("Measuring bandwidth between h1 and h2...")
    result = h1.cmd('iperf -c', h2.IP(), '&')
    print("Bandwidth measurement result:", result)

if __name__ == '__main__':
    setLogLevel('info')
    num_hosts = 4
    net = create_network(num_hosts)
    benchmark_network(net)
