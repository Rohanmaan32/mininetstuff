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

def benchmark_nodes(host_ips):
    results = {}
    for host_ip in host_ips:
        cpu_usage = psutil.cpu_percent(interval=1)
        mem_usage = psutil.virtual_memory().percent
        results[host_ip] = {'cpu_usage': cpu_usage, 'mem_usage': mem_usage}
    return results

def main():
    setLogLevel('info')
    create_network(num_nodes=50)
    host_ips = ['10.0.0.{}'.format(i) for i in range(1, 51)]  # Assuming 50 hosts in the network
    while True:
        results_ping = ping_hosts(host_ips)
        print("Ping Results:")
        print("Host\t\tPacket Loss (%) \tAverage RTT (ms)")
        print("---------------------------------------------------")
        for host_ip, data in results_ping.items():
            print(f"{host_ip}\t\t{data['packet_loss']:.2f}\t\t\t{data['avg_rtt']:.2f}")
        print("---------------------------------------------------")
        
        results_benchmark = benchmark_nodes(host_ips)
        print("\nBenchmark Results:")
        print("Host\t\tCPU Usage (%) \tMemory Usage (%)")
        print("---------------------------------------------------")
        for host_ip, data in results_benchmark.items():
            print(f"{host_ip}\t\t{data['cpu_usage']:.2f}\t\t\t{data['mem_usage']:.2f}")
        print("---------------------------------------------------")
        
        time.sleep(10)  # Sleep for 10 seconds before taking measurements again

if __name__ == "__main__":
    main()
