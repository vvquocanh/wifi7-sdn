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

def random_near(position, delta=5):
    """
    Return a position string close to the given base position.
    :param position: A string in the form "x,y,z".
    :param delta: Maximum deviation in x and y directions.
    :return: A string "new_x,new_y,new_z".
    """
    x, y, z = map(float, position.split(','))
    new_x = x + random.uniform(-delta, delta)
    new_y = y + random.uniform(-delta, delta)
    return f"{new_x},{new_y},{z}"

def start_http_server(net):
    app = Flask(__name__)

    @app.route("/network_metrics", methods=["GET"])
    def get_network_metrics():
        data = []
        for station in net.stations:
            data.append({
                'name': station.name,
                'rssi': get_link_info(station)
            })
        return jsonify(data)

    @app.route("/aps", methods=["GET"])
    def get_aps():
        data = []
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
        for ssid, channel in data.items():
            for ap in net.aps:
                if ap.params['ssid'] == ssid:
                    frequency = channel * 5 + 2407
                    ap.cmd(f"hostapd_cli -i {ap.name}-wlan1 chan_switch {channel} {frequency}")
        return ""
	
    # Run the server on 0.0.0.0 so it’s accessible from any interface.
    app.run(host="0.0.0.0", port=9393)

def get_link_info(station):
    interface = f"{station.name}-wlan0"
    return station.cmd(f'iw dev {interface} link')

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
    ap2 = net.addAccessPoint('ap2', ssid='ap2-ssid', mode='g', channel='1',
                             position=ap2_pos, protocols='OpenFlow13')
    ap3 = net.addAccessPoint('ap3', ssid='ap3-ssid', mode='g', channel='1',
                             position=ap3_pos, protocols='OpenFlow13')
    ap4 = net.addAccessPoint('ap4', ssid='ap4-ssid', mode='g', channel='1',
                             position=ap4_pos, protocols='OpenFlow13')
    ap5 = net.addAccessPoint('ap5', ssid='ap5-ssid', mode='g', channel='1',
                             position=ap5_pos, protocols='OpenFlow13')

    # Create stations for each AP, now positioned near their respective APs.
    # AP1 gets 4 stations.
    sta1 = net.addStation('sta1', ip='10.0.0.1/8', position=random_near(ap1_pos))
    
    # AP2 gets 3 stations.
    sta5 = net.addStation('sta5', ip='10.0.0.5/8', position=random_near(ap2_pos))
    sta6 = net.addStation('sta6', ip='10.0.0.6/8', position=random_near(ap2_pos))
    sta7 = net.addStation('sta7', ip='10.0.0.7/8', position=random_near(ap2_pos))
    
    # AP3 gets 3 stations.
    sta8 = net.addStation('sta8', ip='10.0.0.8/8', position=random_near(ap3_pos))
    sta9 = net.addStation('sta9', ip='10.0.0.9/8', position=random_near(ap3_pos))
    sta10 = net.addStation('sta10', ip='10.0.0.10/8', position=random_near(ap3_pos))
    
    # AP4 gets 2 stations.
    sta11 = net.addStation('sta11', ip='10.0.0.11/8', position=random_near(ap4_pos))
    sta12 = net.addStation('sta12', ip='10.0.0.12/8', position=random_near(ap4_pos))
    
    # AP5 gets 1 station.
    sta13 = net.addStation('sta13', ip='10.0.0.13/8', position=random_near(ap5_pos))
    sta2 = net.addStation('sta2', ip='10.0.0.2/8', position=random_near(ap5_pos))
    sta3 = net.addStation('sta3', ip='10.0.0.3/8', position=random_near(ap5_pos))
    sta4 = net.addStation('sta4', ip='10.0.0.4/8', position=random_near(ap5_pos))
    
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
    
    info("*** Associating stations with their respective APs\n")
    # Associate stations with AP1.
    net.addLink(sta1, ap1)
    
    # Associate stations with AP2.
    net.addLink(sta5, ap2)
    net.addLink(sta6, ap2)
    net.addLink(sta7, ap2)
    
    # Associate stations with AP3.
    net.addLink(sta8, ap3)
    net.addLink(sta9, ap3)
    net.addLink(sta10, ap3)
    
    # Associate stations with AP4.
    net.addLink(sta11, ap4)
    net.addLink(sta12, ap4)
    
    # Associate station with AP5.
    net.addLink(sta13, ap5)
    net.addLink(sta2, ap5)
    net.addLink(sta3, ap5)
    net.addLink(sta4, ap5)
    
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
    
    # Start the HTTP server in a new thread.
    http_thread = threading.Thread(target=start_http_server, args=(net,))
    http_thread.daemon = True
    http_thread.start()
    
    info("*** Running CLI\n")
    CLI(net)
    
    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    custom_topology()
