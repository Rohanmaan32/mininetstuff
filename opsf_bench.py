import subprocess
import time
import psutil
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
    host_ips = []
    for i in range(num_nodes):
        switch = net.addSwitch(f's{i+1}')
        switches.append(switch)
        host = net.addHost(f'h{i+1}', ip=f'10.0.0.{i+1}/24')
        hosts.append(host)
        host_ips.append(f'10.0.0.{i+1}')
        net.addLink(host, switch)
    
    # Connect switches in a linear topology
    for i in range(num_nodes - 1):
        net.addLink(switches[i], switches[i + 1])
    
    # Start network
    net.build()
    c0.start()
    for switch in switches:
        switch.start([c0])
    
    # Start CLI for user interaction
    CLI(net)
    
    # Clean up
    net.stop()

def ping_hosts(host_ips, interval=1, count=10):
    results = {}
    for host_ip in host_ips:
        command = ['ping', '-c', str(count), '-i', str(interval), host_ip]
        ping_output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if ping_output.returncode == 0:
            ping_data = ping_output.stdout
            lines = ping_data.split('\n')
            transmitted = int(lines[0].split()[0])
            received = int(lines[3].split()[3])
            packet_loss = (transmitted - received) / transmitted * 100 if transmitted > 0 else 0
            avg_rtt = float(lines[6].split()[3].split('/')[1])
            results[host_ip] = {'packet_loss': packet_loss, 'avg_rtt': avg_rtt}
        else:
            print(f'Ping to {host_ip} failed')
    return results

def benchmark_forwarding_speed(host_ips):
    results = {}
    for host_ip in host_ips:
        command = ['iperf', '-c', host_ip, '-t', '10']  # Run iperf client for 10 seconds
        iperf_output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if iperf_output.returncode == 0:
            iperf_data = iperf_output.stdout
            lines = iperf_data.split('\n')
            throughput = float(lines[-2].split()[-2])  # Extracting throughput value
            results[host_ip] = throughput
        else:
            print(f'iperf to {host_ip} failed')
    return results

def simulate_link_failure(net, link_to_fail):
    link_to_fail.stop()

def benchmark_convergence_time(net, host_ips):
    # Simulate link failure and measure convergence time
    start_time = time.time()
    simulate_link_failure(net, net.links[0])  # Simulate failure of the first link
    while True:
        ping_results = ping_hosts(host_ips)
        if all(result['packet_loss'] > 0 for result in ping_results.values()):
            break
        time.sleep(1)  # Check ping results every 1 second
    convergence_time = time.time() - start_time
    return convergence_time

def benchmark_convergence_time_with_delay(net, host_ips, delay):
    # Introduce delay on a link and measure convergence time
    link_to_delay = net.links[0]  # Assume the first link for simplicity
    link_to_delay.intf1.config(delay=f'{delay}ms')
    start_time = time.time()
    while True:
        ping_results = ping_hosts(host_ips)
        if all(result['packet_loss'] > 0 for result in ping_results.values()):
            break
        time.sleep(1)  # Check ping results every 1 second
    convergence_time = time.time() - start_time
    return convergence_time

def main():
    setLogLevel('info')
    net = create_network(num_nodes=50)
    host_ips = ['10.0.0.{}'.format(i) for i in range(1, 51)]  # Assuming 50 hosts in the network
    
    # Benchmark node forwarding speed
    forwarding_speed_results = benchmark_forwarding_speed(host_ips)
    print("\nNode Forwarding Speed (Throughput):")
    print("Host IP\t\tThroughput (Mbps)")
    print("-------------------------------------")
    for host_ip, throughput in forwarding_speed_results.items():
        print(f"{host_ip}\t\t{throughput:.2f}")
    print("-------------------------------------")
    
    # Benchmark routing convergence time
    convergence_time = benchmark_convergence_time(net, host_ips)
    print(f"\nRouting Convergence Time: {convergence_time} seconds")

    # Benchmark routing convergence time under different link delay
    delay_values = [10, 50, 100]  # Example delay values in milliseconds
    print("\nRouting Convergence Time Under Different Link Delay:")
    print("Link Delay (ms)\tConvergence Time (s)")
    print("----------------------------------------")
    for delay in delay_values:
        convergence_time = benchmark_convergence_time_with_delay(net, host_ips, delay)
        print(f"{delay}\t\t\t{convergence_time}")
    print("----------------------------------------")

if __name__ == "__main__":
    main()
