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
    net.addStation('sta11', position='10,20,0')
    net.addStation('sta12', position='15,25,0')
    net.addStation('sta13', position='20,30,0')
    
    net.addStation('sta21', position='30,40,0')
    net.addStation('sta22', position='35,45,0')
    net.addStation('sta23', position='40,50,0')
    
    net.addStation('sta31', position='50,60,0')
    net.addStation('sta32', position='55,65,0')
    net.addStation('sta33', position='60,70,0')
    
    ap1 = net.addAccessPoint('ap1', ssid='ssid-ap1', mode='g', channel='1', position='10,30,0')
    ap2 = net.addAccessPoint('ap2', ssid='ssid-ap2', mode='g', channel='6', position='60,30,0')
    ap3 = net.addAccessPoint('ap3', ssid='ssid-ap3', mode='g', channel='11', position='120,100,0')
    
    c1 = net.addController('c1')
    
    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=3.5)
    
    info("*** Configuring nodes\n")
    net.configureNodes()
    
    info("*** Creating links\n")
    net.addLink(ap1, ap2)
    net.addLink(ap2, ap3)
    
    if '-p' not in args:
        net.plotGraph(min_x=-100, min_y=-100, max_x=200, max_y=200)
    
    info("*** Starting network\n")
    net.build()
    c1.start()
    ap1.start([c1])
    ap2.start([c1])
    ap3.start([c1])
    
    info("*** Running CLI\n")
    CLI(net)
    
    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology(sys.argv)
