#!/usr/bin/python

import os
from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.cli import CLI
from mn_wifi.replaying import ReplayingNetworkConditions
from sys import version_info as py_version_info


def topology():

    "Create a network."
    net = Mininet_wifi()

    info("*** Creating nodes\n")
    # Adding stations and setting IP addresses
    sta1 = net.addStation('sta1', mac='00:00:00:00:00:01', ip='192.168.0.1/24', position='47.28,50,0')
    sta2 = net.addStation('sta2', mac='00:00:00:00:00:02', ip='192.168.0.2/24', position='54.08,50,0')
    
    # Adding Access Points
    ap1 = net.addAccessPoint('ap1', ssid='ap-ssid1', mode='g', channel='1', position='50,50,0')
    
    # Adding a controller
    c0 = net.addController('c0', port=6653)

    info("*** Configuring nodes\n")
    net.configureNodes()

    info("*** Starting network\n")
    net.build()
    c0.start()
    ap1.start([c0])

    # Enable monitor mode on the stations for packet capture (optional for network analysis)
    sta1.cmd('iw dev sta1-wlan0 interface add mon0 type monitor')
    sta1.cmd('ip link set mon0 up')
    sta2.cmd('iw dev sta2-wlan0 interface add mon0 type monitor')
    sta2.cmd('ip link set mon0 up')

    # If Python 2.x, serve content with SimpleHTTPServer; if Python 3.x, use http.server
    if py_version_info < (3, 0):
        sta2.cmd('pushd ~/; python -m SimpleHTTPServer 80 &')
    else:
        sta2.cmd('pushd ~/; python -m http.server 80 &')

    # Define the path for the network traces
    path = os.path.dirname(os.path.abspath(__file__)) + '/replayingNetworkConditions/'

    # Get the network traces (this can be customized based on your specific scenario)
    get_trace(sta1, '{}clientTrace.txt'.format(path))
    get_trace(sta2, '{}serverTrace.txt'.format(path))

    info("*** Replaying Network Conditions\n")
    ReplayingNetworkConditions(net)

    # Running iperf test between stations to measure network performance
    info("*** Running iperf to measure network performance\n")
    sta2.cmd('iperf -s &')  # Start iperf server on sta2
    sta1.cmd('iperf -c ' + sta2.IP() + ' -i 1 -t 60 > sta1_iperf_output.txt &')  # Start iperf client on sta1, connect to sta2

    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()


def get_trace(node, file):
    """Get the network trace and extract time, bandwidth, loss, and latency."""
    file = open(file, 'r')
    raw_data = file.readlines()
    file.close()

    node.time = []
    node.bw = []
    node.loss = []
    node.delay = []
    node.latency = []

    for data in raw_data:
        line = data.split()
        node.time.append(float(line[0]))  # First column = Time
        node.bw.append(((float(line[1])) / 1000000) / 2)  # Second column = BW (converted to Mbps)
        node.loss.append(float(line[2]))  # Loss
        node.latency.append(float(line[3]))  # Latency


if __name__ == '__main__':
    setLogLevel('info')
    topology()
