import sys
from mininet.node import Controller
from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference
import time
import threading

def log_metrics(net):
    with open("network_metrics.log", "w") as log_file:
        log_file.write("Time,Node,RSSI,Channel,TrafficLoad,ConnectedDevices,Interference,PacketLoss,Latency\n")
        while True:
            for ap in net.aps:
                rssi = ap.params.get('rssi', 'N/A')
                channel = ap.params.get('channel', 'N/A')
                traffic_load = ap.params.get('txpower', 'N/A')  # Example, use realistic metric
                connected_devices = len(ap.associatedStations)
                interference = ap.params.get('interference', 'N/A')
                packet_loss = ap.params.get('loss', 'N/A')  # Placeholder
                latency = ap.params.get('latency', 'N/A')  # Placeholder
                
                log_file.write(f"{time.time()},{ap.name},{rssi},{channel},{traffic_load},{connected_devices},{interference},{packet_loss},{latency}\n")
                log_file.flush()
            time.sleep(5)

def topology(args):
    net = Mininet_wifi(controller=Controller, link=wmediumd, wmediumd_mode=interference)
    
    info("*** Creating nodes\n")
    net.addStation('sta11', position='10,20,0')
    net.addStation('sta12', position='15,25,0')
    net.addStation('sta13', position='20,30,0')
    
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
    
    thread = threading.Thread(target=log_metrics, args=(net,))
    thread.daemon = True
    thread.start()
    
    info("*** Running CLI\n")
    CLI(net)
    
    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology(sys.argv)
