#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call

class CustomTopology(Topo):
    '''
        Chương trình tạo mạng SDN/OpenFlow với topology gồm:
        - 1 controller
        - 4 switch 
        - 16 host
    '''

    def build(self):
        # Thêm Controller (C0) - sẽ được kết nối khi chạy mininet
        
        # Thêm các switch S1, S2, S3, S4
        s1 = self.addSwitch('s1', cls=OVSKernelSwitch)
        s2 = self.addSwitch('s2', cls=OVSKernelSwitch)
        s3 = self.addSwitch('s3', cls=OVSKernelSwitch)
        s4 = self.addSwitch('s4', cls=OVSKernelSwitch)
        
        # Thêm các host và kết nối với switch tương ứng
        # Hosts kết nối với S1
        h1 = self.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
        h2 = self.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)
        h3 = self.addHost('h3', cls=Host, ip='10.0.0.3', defaultRoute=None)
        h4 = self.addHost('h4', cls=Host, ip='10.0.0.4', defaultRoute=None)
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)
        self.addLink(h4, s1)
        
        # Hosts kết nối với S2
        h5 = self.addHost('h5', cls=Host, ip='10.0.0.5', defaultRoute=None)
        h6 = self.addHost('h6', cls=Host, ip='10.0.0.6', defaultRoute=None)
        h7 = self.addHost('h7', cls=Host, ip='10.0.0.7', defaultRoute=None)
        h8 = self.addHost('h8', cls=Host, ip='10.0.0.8', defaultRoute=None)
        self.addLink(h5, s2)
        self.addLink(h6, s2)
        self.addLink(h7, s2)
        self.addLink(h8, s2)
        
        # Hosts kết nối với S3
        h9 = self.addHost('h9', cls=Host, ip='10.0.0.9', defaultRoute=None)
        h10 = self.addHost('h10', cls=Host, ip='10.0.0.10', defaultRoute=None)
        h11 = self.addHost('h11', cls=Host, ip='10.0.0.11', defaultRoute=None)
        h12 = self.addHost('h12', cls=Host, ip='10.0.0.12', defaultRoute=None)
        self.addLink(h9, s3)
        self.addLink(h10, s3)
        self.addLink(h11, s3)
        self.addLink(h12, s3)
        
        # Hosts kết nối với S4
        h13 = self.addHost('h13', cls=Host, ip='10.0.0.13', defaultRoute=None)
        h14 = self.addHost('h14', cls=Host, ip='10.0.0.14', defaultRoute=None)
        h15 = self.addHost('h15', cls=Host, ip='10.0.0.15', defaultRoute=None)
        h16 = self.addHost('h16', cls=Host, ip='10.0.0.16', defaultRoute=None)
        self.addLink(h13, s4)
        self.addLink(h14, s4)
        self.addLink(h15, s4)
        self.addLink(h16, s4)
        
        # Kết nối giữa các switch để tạo topology
        self.addLink(s1, s2)
        self.addLink(s1, s3)
        self.addLink(s2, s4)
        self.addLink(s3, s4)

def run():
    topo = CustomTopology()
    c0 = RemoteController('c0', ip='127.0.0.1', port=6653)
    net = Mininet(topo=topo, controller=c0)
    
    net.start()
    
    print("*** Dumping host connections")
    dumpNodeConnections(net.hosts)
    
    print("*** Testing network connectivity")
    net.pingAll()
    
    print("*** Running CLI")
    CLI(net)
    
    print("*** Stopping network")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
