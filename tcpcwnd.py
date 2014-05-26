#!/usr/bin/python

"CS 244 Assingment 3: Increasing initial congestion window"

from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.log import lg
from mininet.util import dumpNodeConnections
from mininet.cli import CLI
from mininet.util import pmonitor
from signal import SIGINT

import subprocess
from subprocess import Popen, PIPE
from time import sleep, time
from multiprocessing import Process
import termcolor as T
from argparse import ArgumentParser
import random

import sys
import os
from util.monitor import monitor_qlen
from util.helper import stdev

# Parse arguments
parser = ArgumentParser(description="Cwnd adjusting")

parser.add_argument('-n',
                    dest="n",
                    type=int,
                    action="store",
                    help="Number of nodes in star.  Must be >= 3",
                    required=True)

parser.add_argument('--maxq',
                    dest="maxq",
                    action="store",
                    help="Max buffer size of network interface in packets",
                    default=1000)

parser.add_argument('--cong',
                    dest="cong",
                    help="Congestion control algorithm to use",
                    default="bic")

args = parser.parse_args()

# Topology to be instantiated in Mininet
class StarTopo(Topo):
    "Star topology for Buffer Sizing experiment"

    def __init__(self, n=3, cpu=None, maxq=None):
        # Add default members to class.
        super(StarTopo, self ).__init__()
        self.n = n
        self.cpu = cpu
        self.maxq = maxq
	self.create_topology()

    def create_topology(self):

        # add switch
        switch = self.addSwitch('s0')

        # add hosts and links
        for h in range(self.n):
            hostname = 'h%s' % (h+1)
            host = self.addHost('h%s' % (h + 1))
            bw_inst = getBW()/1000.0    # kbps -> Mbps
            delay_inst = '%fms' % (getRTT()/4)
            
            print "Setting %s-%s link (BW, delay) to (%.2f Mbps, %.2fms)" % (hostname, 's0', bw_inst, delay_inst)            
            linkopts = dict(bw=bw_inst, delay=delay_inst,
                    max_queue_size=self.maxq, htb=True)

            self.addLink(host, switch, **linkopts)
        # Let h1 be the front-end server

def getBW():
    sample = random.uniform(0, 1)
    if sample < 0.25:
        return 200/2.0  # kbps
    elif sample < 0.5:
        return (200+500)/2.0
    elif sample < 0.75:
        return (500+1259)/2.0
    else:
        return (1259+3162)/2.0

def getRTT():
    sample = random.uniform(0, 1)
    if sample < 0.25:
        return 31/2.0
    elif sample < 0.5:
        return (31+70)/2.0
    elif sample < 0.75:
        return (70+120)/2.0
    else:
        return (120+1000)/2.0

def start_receiver(net, hostName):
    print "Starting iperf server at %s ..." % hostName

    #for i in xrange(args.n-1):   # Can we get number of nodes from <net>?
    h = net.getNodeByName(hostName)
    client = h.popen('iperf -s -w %d' % 50000, shell=True)    # 50kB TCP window

def set_init_cwnd(net, num_seg):
    ''' --How to change initial cwnd--
        ip route show
        sudo ip route change [Paste the current settings for default] initcwnd 10
    '''

    print "Changing initcwnd of h1(server) to %d..." % num_seg  
    
    h1 = net.getNodeByName('h1')

    result = h1.cmd('ip route show')
    result = result.rstrip('\n')
    print result
    result = h1.cmd('ip route change %s initcwnd %d' % (result.rstrip('\n'), num_seg))
    
    # Verify
    result = h1.cmd('ip route show')
    result = result.rstrip('\n')
    print result

def run_iperfs(net, destHost):
    h1 = net.getNodeByName('h1')
    #for i in xrange(args.net-1):
    #    h = net.getNodeByName('h%d' % i+2)

    h = net.getNodeByName(destHost)    
    size = get_response_size()
    client = h.popen('iperf -c %s -n %s' % (h.IP(), size))
    # Need to give random size of flow based on distribution    
    # Also make it send sequentially

def get_response_size():    # returns in bytes
    sample = random.uniform(0, 1)
    if sample < 0.25:
        return 200
    elif sample < 0.5:
        return 1500
    elif sample < 0.75:
        return 5000
    else:
        return 50000

def plot_latency():
    pass

def main():
    "Create network and run Buffer Sizing experiment"

    start = time()
    # Reset to known state
    topo = StarTopo(n=args.n, maxq=args.maxq)
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
    net.start()
    dumpNodeConnections(net.hosts)
    net.pingAll()

    # Start iperf servers in users
    #start_receiver(net)

    # Set initial congestion window to three
    set_init_cwnd(net, 3)
    # Experiment
    for i in xrange(args.n-1):
        destHost = "h%d"%(i+2)
        start_receiver(net, destHost)
        run_iperfs(net, destHost)

    # Set initial congestion window to ten
    #set_init_cwnd(net, 10)
    # Experiment
    #run_iperfs(net)

    # How do we collect latency 

    # Plot graph
    #plot_latency()

if __name__ == '__main__':
    try:
        main()
    except:
        print "-"*80
        print "Caught exception.  Cleaning up..."
        print "-"*80
        import traceback
        traceback.print_exc()
        os.system("killall -9 top bwm-ng tcpdump cat mnexec iperf; mn -c")
