#!/usr/bin/python

from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP
from mininet.node import RemoteController
from mn_wifi.cli import CLI
from mininet.log import setLogLevel, info
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference

import threading
import random
from flask import Flask, jsonify, request

def random_position():

    new_x = random.uniform(0, 100)
    new_y = random.uniform(0, 100)
    return f"{new_x},{new_y},0"

def start_http_server(net):
    app = Flask(__name__)
    
    # Add a lock for synchronizing access to network nodes
    ap_lock = threading.Lock()

    @app.route("/aps", methods=["GET"])
    def get_aps():
        data = []
        with ap_lock:
            for ap in net.aps:
                data.append({
                    'name': ap.name,
                    'ssid': ap.params['ssid'],
                    'position': ap.position,
                })
        return jsonify(data)
    
    @app.route("/aps/channel", methods=["POST"])
    def adjust_channel():
        data = request.get_json()
        with ap_lock:
            for ssid, channel in data.items():
                for ap in net.aps:
                    if ap.params['ssid'] == ssid:
                        frequency = channel * 5 + 2407
                        try:
                            # Make sure the AP is ready for commands
                            if ap.shell and not ap.waiting:
                                # Send the command and wait for it to complete
                                ap.cmd(f"hostapd_cli -i {ap.name}-wlan1 chan_switch {channel} {frequency}")
                                ap.waitOutput()
                            else:
                                # If AP is busy, wait briefly and try again
                                time.sleep(0.5)
                                if ap.shell and not ap.waiting:
                                    ap.cmd(f"hostapd_cli -i {ap.name}-wlan1 chan_switch {channel} {frequency}")
                                    ap.waitOutput()
                        except Exception as e:
                            info(f"Error adjusting channel for {ap.name}: {str(e)}\n")
        return jsonify({"status": "success"})

    def get_link_info(station):
        output = station.cmd(f'iw dev {station.name}-wlan0 link')
        station.waitOutput()
        return output
    
    # Run the server on 0.0.0.0 so it's accessible from any interface.
    app.run(host="0.0.0.0", port=9393)

def get_link_info(station):
    interface = f"{station.name}-wlan0"
    return station.cmd(f'iw dev {interface} link')

def start_server(net):
	# Start the HTTP server in a new thread.
    http_thread = threading.Thread(target=start_http_server, args=(net,))
    http_thread.daemon = True
    http_thread.start()

def custom_topology():

    "Create a custom topology on a 200x200 map with 5 APs and stations close to their APs."
    net = Mininet_wifi(controller=RemoteController, link=wmediumd,
                       wmediumd_mode=interference, noise_th=-91, fading_cof=3,
                       accessPoint=OVSKernelAP)

    info("*** Creating nodes\n")
    
    # Define AP positions
    ap1_pos = '25,25,0'
    ap2_pos = '25,75,0'
    ap3_pos = '75,25,0'
    ap4_pos = '75,75,0'
    ap5_pos = '50,50,0'
    
    # Create 5 access points equally distributed on a 200x200 map.
    ap1 = net.addAccessPoint('ap1', ssid='ap1-ssid', mode='g', channel='1',
                             position=ap1_pos, protocols='OpenFlow13')
    ap2 = net.addAccessPoint('ap2', ssid='ap2-ssid', mode='g', channel='2',
                             position=ap2_pos, protocols='OpenFlow13')
    ap3 = net.addAccessPoint('ap3', ssid='ap3-ssid', mode='g', channel='3',
                             position=ap3_pos, protocols='OpenFlow13')
    ap4 = net.addAccessPoint('ap4', ssid='ap4-ssid', mode='g', channel='4',
                             position=ap4_pos, protocols='OpenFlow13')
    ap5 = net.addAccessPoint('ap5', ssid='ap5-ssid', mode='g', channel='5',
                             position=ap5_pos, protocols='OpenFlow13')
	
    for i in range(1, 21):
        net.addStation(f'sta{i}', ip=f'10.0.0.{i}/8', position=random_position())
    
    info("*** Creating remote controller\n")
    c0 = net.addController('c0', controller=RemoteController,
                           ip='192.168.1.3', port=6633)
    
    # Set the mobility model with max coordinates of 200x200.
    #net.setMobilityModel(time=0, model='RandomDirection',
                          #max_x=100, max_y=100, seed=25, ac_method='ssf')
    
    net.setPropagationModel(model="logDistance", exp=4)
    
    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()
    
    # Uncomment the next line if you want a visual plot.
    net.plotGraph(max_x=100, max_y=100)
    
    info("*** Connecting APs in a star topology (using AP5 as the central node)\n")
    net.addLink(ap1, ap5)
    net.addLink(ap2, ap5)
    net.addLink(ap3, ap5)
    net.addLink(ap4, ap5)
    
    info("*** Starting network\n")
    net.build()
    c0.start()
    ap1.start([c0])
    ap2.start([c0])
    ap3.start([c0])
    ap4.start([c0])
    ap5.start([c0])
    
    start_server(net)
    
    info("*** Running CLI\n")
    CLI(net)
    
    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    custom_topology()
