import sys
from mininet.node import Controller
from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference

def topology(args):
    net = Mininet_wifi(controller=Controller, link=wmediumd, wmediumd_mode=interference)
    
    info("*** Creating nodes\n")
    # Adding two stations per access point
    net.addStation('sta11', position='10,20,0')
    net.addStation('sta12', position='15,25,0')
    
    net.addStation('sta21', position='50,60,0')
    net.addStation('sta22', position='55,65,0')
    
    # Adding two access points
    ap1 = net.addAccessPoint('ap1', ssid='ssid-ap1', mode='g', channel='1', position='10,30,0')
    ap2 = net.addAccessPoint('ap2', ssid='ssid-ap2', mode='g', channel='6', position='50,30,0')
    
    # Adding controller
    c1 = net.addController('c1')
    
    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=3.5)
    
    info("*** Configuring nodes\n")
    net.configureNodes()
    
    info("*** Creating links\n")
    net.addLink(ap1, ap2)
    
    if '-p' not in args:
        net.plotGraph(min_x=-100, min_y=-100, max_x=200, max_y=200)
    
    info("*** Starting network\n")
    net.build()
    c1.start()
    ap1.start([c1])
    ap2.start([c1])
    
    # Run iperf to collect performance metrics between stations
    info("*** Running iperf to collect metrics\n")
    # Perform a TCP test between stations (no need to specify port)
    CLI.do_iperf('sta11', 'sta12')  # Station1 to Station2 on ap1
    CLI.do_iperf('sta21', 'sta22')  # Station1 to Station2 on ap2
    
    info("*** Running CLI for user interaction\n")
    CLI(net)
    
    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology(sys.argv)
