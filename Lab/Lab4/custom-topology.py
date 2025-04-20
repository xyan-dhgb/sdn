from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink

def create_topology():
    net = Mininet(controller=RemoteController, switch=OVSKernelSwitch, link=TCLink)
    
    # Add controller
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6653)
    
    # Add switches and hosts 
    switches = [net.addSwitch(f's{i}') for i in range(1, 5)]
    hosts = [net.addHost(f'h{i}') for i in range(1, 17)]
    
    # Create links between switches and hosts
    for i, switch in enumerate(switches):
        for j in range(i + 1, len(switches)):
            net.addLink(switch, switches[j])
    
    # Create links between switches
    for i, switch in enumerate(switches):
        for j in range(4):
            net.addLink(switch, hosts[i * 4 + j])
    
    # Build the network topology and start the controller
    net.build()
    c0.start()
    
    # Start switches
    for switch in switches:
        switch.start([c0])
    
    return net

if __name__ == '__main__':
    setLogLevel('info')
    net = create_topology()
    CLI(net)
    net.stop()