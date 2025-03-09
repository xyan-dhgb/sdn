from mininet.topo import Topo

class MyTopo(Topo):
    "Custom topology cho lab SDN với 4 switch và 4 host"

    def build(self):
        # Thêm 4 switch
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        # Thêm 4 host
        h1 = self.addHost('h1', mac='00:00:00:00:00:01')
        h2 = self.addHost('h2', mac='00:00:00:00:00:02')
        h3 = self.addHost('h3', mac='00:00:00:00:00:03')
        h4 = self.addHost('h4', mac='00:00:00:00:00:04')

        # Thêm liên kết giữa switch và host
        self.addLink(s1, h1)
        self.addLink(s2, h2)
        self.addLink(s3, h3)
        self.addLink(s4, h4)
        
        # Kết nối các switch với nhau (mô phỏng liên kết từ controller)
        self.addLink(s1, s2)
        self.addLink(s1, s3)
        self.addLink(s1, s4)
        self.addLink(s2, s3)
        self.addLink(s2, s4)
        self.addLink(s3, s4)

# Định nghĩa topology để Mininet có thể tải
topos = {'mytopo': (lambda: MyTopo())}