import subprocess
import time

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

def main():
    host_ips = ['10.0.0.{}'.format(i) for i in range(1, 51)]  # Assuming 50 hosts in the network
    while True:
        results = ping_hosts(host_ips)
        print("Host\t\tPacket Loss (%) \tAverage RTT (ms)")
        print("---------------------------------------------------")
        for host_ip, data in results.items():
            print(f"{host_ip}\t\t{data['packet_loss']:.2f}\t\t\t{data['avg_rtt']:.2f}")
        print("---------------------------------------------------")
        time.sleep(10)  # Sleep for 10 seconds before taking measurements again

if __name__ == "__main__":
    main()
