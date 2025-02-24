from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP
from mininet.node import RemoteController
from mn_wifi.cli import CLI
from mininet.log import setLogLevel, info

def linear_topology():
    "Create a linear topology with 3 access points and one station per AP."
    # Use OVSKernelAP to ensure OpenFlow13 support and client isolation
    net = Mininet_wifi(controller=RemoteController,
                       accessPoint=OVSKernelAP)

    info("*** Creating nodes\n")
    # Create three access points with client isolation enabled.
    ap1 = net.addAccessPoint('ap1', ssid='ap1-ssid', mode='g', channel='1',
                             position='10,10,0',
                             protocols='OpenFlow13')
    ap2 = net.addAccessPoint('ap2', ssid='ap2-ssid', mode='g', channel='6',
                             position='30,10,0',
                             protocols='OpenFlow13')
    ap3 = net.addAccessPoint('ap3', ssid='ap3-ssid', mode='g', channel='11',
                             position='50,10,0',
                             protocols='OpenFlow13')

# Create 3 stations for AP1
    sta1 = net.addStation('sta1', ip='10.0.0.1/8', position='8,15,0')
    sta2 = net.addStation('sta2', ip='10.0.0.2/8', position='10,15,0')
    sta3 = net.addStation('sta3', ip='10.0.0.3/8', position='12,15,0')

    # Create 3 stations for AP2
    sta4 = net.addStation('sta4', ip='10.0.0.4/8', position='28,15,0')
    sta5 = net.addStation('sta5', ip='10.0.0.5/8', position='30,15,0')
    sta6 = net.addStation('sta6', ip='10.0.0.6/8', position='32,15,0')

    # Create 3 stations for AP3
    sta7 = net.addStation('sta7', ip='10.0.0.7/8', position='48,15,0')
    sta8 = net.addStation('sta8', ip='10.0.0.8/8', position='50,15,0')
    sta9 = net.addStation('sta9', ip='10.0.0.9/8', position='52,15,0')

    info("*** Creating remote controller\n")
    c0 = net.addController('c0', controller=RemoteController,
                           ip='192.168.1.3', port=6633)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info("*** Associating stations with their respective APs\n")
    # Associate stations with AP1
    net.addLink(sta1, ap1)
    net.addLink(sta2, ap1)
    net.addLink(sta3, ap1)
    
    # Associate stations with AP2
    net.addLink(sta4, ap2)
    net.addLink(sta5, ap2)
    net.addLink(sta6, ap2)
    
    # Associate stations with AP3
    net.addLink(sta7, ap3)
    net.addLink(sta8, ap3)
    net.addLink(sta9, ap3)

    info("*** Connecting APs in a linear topology\n")
    net.addLink(ap1, ap2)
    net.addLink(ap2, ap3)

    info("*** Starting network\n")
    net.build()
    c0.start()
    ap1.start([c0])
    ap2.start([c0])
    ap3.start([c0])

    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    linear_topology()