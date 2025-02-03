from mininet.node import Controller
from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI_wifi
from mn_wifi.net import Mininet_wifi
import time

# Function to log network metrics
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

# Mininet-WiFi network setup
def topology():
    net = Mininet_wifi(controller=Controller)
    
    info("*** Adding controller\n")
    c0 = net.addController('c0', controller=Controller)
    
    info("*** Adding access points\n")
    ap1 = net.addAccessPoint('ap1', ssid='ssid-ap1', mode='g', channel='1')
    ap2 = net.addAccessPoint('ap2', ssid='ssid-ap2', mode='g', channel='6')
    ap3 = net.addAccessPoint('ap3', ssid='ssid-ap3', mode='g', channel='11')
    
    info("*** Adding stations\n")
    sta11 = net.addStation('sta11', ip='10.0.0.11', position='10,20,0')
    sta12 = net.addStation('sta12', ip='10.0.0.12', position='15,25,0')
    sta13 = net.addStation('sta13', ip='10.0.0.13', position='20,30,0')
    
    sta21 = net.addStation('sta21', ip='10.0.0.21', position='30,40,0')
    sta22 = net.addStation('sta22', ip='10.0.0.22', position='35,45,0')
    sta23 = net.addStation('sta23', ip='10.0.0.23', position='40,50,0')
    
    sta31 = net.addStation('sta31', ip='10.0.0.31', position='50,60,0')
    sta32 = net.addStation('sta32', ip='10.0.0.32', position='55,65,0')
    sta33 = net.addStation('sta33', ip='10.0.0.33', position='60,70,0')
    
    info("*** Configuring WiFi nodes\n")
    net.configureWifiNodes()
    
    info("*** Creating links\n")
    net.addLink(sta11, ap1)
    net.addLink(sta12, ap1)
    net.addLink(sta13, ap1)
    
    net.addLink(sta21, ap2)
    net.addLink(sta22, ap2)
    net.addLink(sta23, ap2)
    
    net.addLink(sta31, ap3)
    net.addLink(sta32, ap3)
    net.addLink(sta33, ap3)
    
    info("*** Starting network\n")
    net.build()
    c0.start()
    ap1.start([c0])
    ap2.start([c0])
    ap3.start([c0])
    
    # Start logging metrics in a separate thread
    import threading
    thread = threading.Thread(target=log_metrics, args=(net,))
    thread.daemon = True
    thread.start()
    
    info("*** Running CLI\n")
    CLI_wifi(net)
    
    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology()
