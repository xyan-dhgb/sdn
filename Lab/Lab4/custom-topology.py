#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.node import OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import time

class ImprovedCustomTopo(Topo):
    "Create a custom topology for SDN/OpenFlow with guaranteed connectivity."

    def build(self):
        # Add switches
        s1 = self.addSwitch('s1', cls=OVSKernelSwitch, protocols='OpenFlow13')
        s2 = self.addSwitch('s2', cls=OVSKernelSwitch, protocols='OpenFlow13')
        s3 = self.addSwitch('s3', cls=OVSKernelSwitch, protocols='OpenFlow13')
        s4 = self.addSwitch('s4', cls=OVSKernelSwitch, protocols='OpenFlow13')
        
        # Add hosts and connect them to switches
        # Hosts for S1
        h1 = self.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
        h2 = self.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02')
        h3 = self.addHost('h3', ip='10.0.0.3/24', mac='00:00:00:00:00:03')
        h4 = self.addHost('h4', ip='10.0.0.4/24', mac='00:00:00:00:00:04')
        self.addLink(h1, s1, bw=10, delay='1ms')
        self.addLink(h2, s1, bw=10, delay='1ms')
        self.addLink(h3, s1, bw=10, delay='1ms')
        self.addLink(h4, s1, bw=10, delay='1ms')
        
        # Hosts for S2
        h5 = self.addHost('h5', ip='10.0.0.5/24', mac='00:00:00:00:00:05')
        h6 = self.addHost('h6', ip='10.0.0.6/24', mac='00:00:00:00:00:06')
        h7 = self.addHost('h7', ip='10.0.0.7/24', mac='00:00:00:00:00:07')
        h8 = self.addHost('h8', ip='10.0.0.8/24', mac='00:00:00:00:00:08')
        self.addLink(h5, s2, bw=10, delay='1ms')
        self.addLink(h6, s2, bw=10, delay='1ms')
        self.addLink(h7, s2, bw=10, delay='1ms')
        self.addLink(h8, s2, bw=10, delay='1ms')
        
        # Hosts for S3
        h9 = self.addHost('h9', ip='10.0.0.9/24', mac='00:00:00:00:00:09')
        h10 = self.addHost('h10', ip='10.0.0.10/24', mac='00:00:00:00:00:0A')
        h11 = self.addHost('h11', ip='10.0.0.11/24', mac='00:00:00:00:00:0B')
        h12 = self.addHost('h12', ip='10.0.0.12/24', mac='00:00:00:00:00:0C')
        self.addLink(h9, s3, bw=10, delay='1ms')
        self.addLink(h10, s3, bw=10, delay='1ms')
        self.addLink(h11, s3, bw=10, delay='1ms')
        self.addLink(h12, s3, bw=10, delay='1ms')
        
        # Hosts for S4
        h13 = self.addHost('h13', ip='10.0.0.13/24', mac='00:00:00:00:00:0D')
        h14 = self.addHost('h14', ip='10.0.0.14/24', mac='00:00:00:00:00:0E')
        h15 = self.addHost('h15', ip='10.0.0.15/24', mac='00:00:00:00:00:0F')
        h16 = self.addHost('h16', ip='10.0.0.16/24', mac='00:00:00:00:00:10')
        self.addLink(h13, s4, bw=10, delay='1ms')
        self.addLink(h14, s4, bw=10, delay='1ms')
        self.addLink(h15, s4, bw=10, delay='1ms')
        self.addLink(h16, s4, bw=10, delay='1ms')
        
        # Connect switches in a mesh topology as shown in the image
        self.addLink(s1, s2, bw=20, delay='2ms')
        self.addLink(s2, s3, bw=20, delay='2ms')
        self.addLink(s3, s4, bw=20, delay='2ms')

        
        # Remove the direct link between s1 and s3 as it's not in the image

def setup_network():
    "Create network and run simple performance tests"
    topo = ImprovedCustomTopo()
    
    # Create network with remote controller
    net = Mininet(topo=topo, 
                  controller=RemoteController('c0', ip='127.0.0.1', port=6653),
                  link=TCLink,
                  autoSetMacs=True)
    
    # Start network
    net.start()
    
    # Wait a bit for the network to settle
    info('*** Waiting for network to settle\n')
    time.sleep(5)
    
    # Configure all hosts - set default route
    for host in net.hosts:
        host.cmd('ip route add default via 10.0.0.254')
    
    # Pre-ARP all hosts to avoid initial ARP broadcast delays
    info('*** Pre-populating ARP caches\n')
    for h1 in net.hosts:
        for h2 in net.hosts:
            if h1 != h2:
                h1.cmd('ping -c 1 ' + h2.IP())
    
    info('*** Running CLI\n')
    CLI(net)
    
    # Stop network
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    setup_network()