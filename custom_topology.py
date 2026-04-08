#!/usr/bin/env python3

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info

class OrangeTopology(Topo):
    """
    Custom Topology for the Orange Problem.
    Contains 2 Switches and 4 Hosts.
    """
    def build(self):
        # 1. Add Switches
        # We use Open vSwitch (OVS), which supports OpenFlow
        s1 = self.addSwitch('s1', cls=OVSSwitch)
        s2 = self.addSwitch('s2', cls=OVSSwitch)

        # 2. Add Hosts
        h1 = self.addHost('h1', ip='10.0.0.1/24')
        h2 = self.addHost('h2', ip='10.0.0.2/24')
        h3 = self.addHost('h3', ip='10.0.0.3/24')
        h4 = self.addHost('h4', ip='10.0.0.4/24')

        # 3. Create Links (Connect Hosts to Switches)
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(h4, s2)

        # 4. Create Link (Connect Switches together)
        self.addLink(s1, s2)

def run():
    # Set the log level to 'info' to see what Mininet is doing
    setLogLevel('info')
    
    info('*** Creating network\n')
    topo = OrangeTopology()
    
    # CRITICAL: Define the Remote Controller
    # This tells the network to look for your Ryu/POX controller on port 6633/6653
    net = Mininet(topo=topo, controller=lambda name: RemoteController(name, ip='127.0.0.1', port=6633), switch=OVSSwitch)
    
    info('*** Starting network\n')
    net.start()
    
    info('*** Running CLI\n')
    # Opens the Mininet command line so you can run pings and tests
    CLI(net)
    
    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    run()
