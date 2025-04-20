#!/usr/bin/env python3

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ether_types
from ryu.lib import hub
from operator import attrgetter
import time

class NetworkMonitor(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(NetworkMonitor, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)
        
        # Time interval for sending stats requests (seconds) - can be changed to 1 second if needed
        self.stats_interval = 10  
        
        # Store port stats information
        self.port_stats = {}
        # Store flow stats information
        self.flow_stats = {}
        
        self.logger.info("Network Monitor initialized with interval: %s seconds", self.stats_interval)

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        """
        Monitor the connection state of datapaths (switches)
        and update the datapaths list
        """
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.info('Datapath registered: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.info('Datapath unregistered: %016x', datapath.id)
                del self.datapaths[datapath.id]

    def _monitor(self):
        """
        Main thread to send statistics requests to switches
        periodically based on stats_interval
        """
        while True:
            self.logger.info("\n=== Requesting statistics from switches ===")
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(self.stats_interval)

    def _request_stats(self, datapath):
        """
        Send statistics request to the switch
        """
        self.logger.debug('Sending stats request to datapath: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Send Flow Statistics Request
        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

        # Send Port Statistics Request
        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        """
        Handle switch connection and feature message
        Install default flow for the switch
        """
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Install table-miss flow entry
        match = parser.OFPMatch()  # match all packets
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)
        self.logger.info("Switch %016x connected", datapath.id)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None, idle_timeout=0, hard_timeout=0):
        """
        Add a flow entry to the switch's flow table
        """
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst, idle_timeout=idle_timeout,
                                    hard_timeout=hard_timeout)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst,
                                    idle_timeout=idle_timeout, hard_timeout=hard_timeout)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        """
        Handle packets sent to the controller (learn MAC addresses and install flows)
        """
        # Get packet and switch information
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        # Parse packet
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        # Ignore LLDP packets
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return
        
        # Ignore IPv6 packets
        if eth.ethertype == ether_types.ETH_TYPE_IPV6:
            return

        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        
        # Initialize dictionary for dpid if not present
        if dpid not in self.mac_to_port:
            self.mac_to_port[dpid] = {}

        # Learn source MAC address and corresponding port
        self.mac_to_port[dpid][src] = in_port

        # Check if destination port is known
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            # If unknown, flood the packet
            out_port = ofproto.OFPP_FLOOD

        # Prepare actions for the packet
        actions = [parser.OFPActionOutput(out_port)]

        # Install flow if not flooding
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            # Use timeout to ensure flows can be updated
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 1, match, actions, msg.buffer_id, idle_timeout=20, hard_timeout=60)
                return
            else:
                self.add_flow(datapath, 1, match, actions, idle_timeout=20, hard_timeout=60)

        # Send the packet out to the corresponding port
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                 in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

        # Log packet information
        self.logger.info("Packet in %s %s %s %s", dpid, src, dst, in_port)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        """
        Handle Flow Statistics reply from the switch
        """
        body = ev.msg.body
        dpid = ev.msg.datapath.id
        
        # Store flow stats information in dictionary
        if dpid not in self.flow_stats:
            self.flow_stats[dpid] = {}
        
        self.logger.info("\n=== Flow Stats Reply from Switch %016x ===", dpid)
        self.logger.info("%-12s %-18s %-18s %-8s %-10s %-10s",
                         'In-Port', 'Src-MAC', 'Dst-MAC', 'Out-Port', 'Packets', 'Bytes')
        self.logger.info("-" * 80)
        
        # Only consider flows with priority > 0 (ignore table-miss)
        for stat in sorted([flow for flow in body if flow.priority > 0],
                           key=lambda flow: (flow.match.get('in_port', 0))):
            if 'in_port' in stat.match and 'eth_dst' in stat.match and 'eth_src' in stat.match:
                in_port = stat.match['in_port']
                eth_src = stat.match['eth_src']
                eth_dst = stat.match['eth_dst']
                out_port = stat.instructions[0].actions[0].port
                packets = stat.packet_count
                bytes = stat.byte_count
                
                # Store information in dictionary
                flow_id = "{}-{}-{}".format(in_port, eth_src, eth_dst)
                self.flow_stats[dpid][flow_id] = {
                    'in_port': in_port,
                    'eth_src': eth_src,
                    'eth_dst': eth_dst,
                    'out_port': out_port,
                    'packets': packets,
                    'bytes': bytes,
                    'timestamp': time.time()
                }
                
                # Print flow stats information
                self.logger.info("%-12d %-18s %-18s %-8d %-10d %-10d",
                                 in_port, eth_src, eth_dst, out_port, packets, bytes)

    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        """
        Handle Port Statistics reply from the switch
        """
        body = ev.msg.body
        dpid = ev.msg.datapath.id
        
        # Store port stats information in dictionary
        if dpid not in self.port_stats:
            self.port_stats[dpid] = {}
            
        self.logger.info("\n=== Port Stats Reply from Switch %016x ===", dpid)
        self.logger.info("%-8s %-12s %-12s %-12s %-12s %-12s %-12s",
                         'Port', 'Rx-Packets', 'Rx-Bytes', 'Rx-Errors', 'Tx-Packets', 'Tx-Bytes', 'Tx-Errors')
        self.logger.info("-" * 80)
        
        # Parse information from each port
        for stat in sorted(body, key=attrgetter('port_no')):
            # Skip local port
            if stat.port_no == 4294967294:  # OFPP_LOCAL
                continue
                
            port_no = stat.port_no
            rx_packets = stat.rx_packets
            rx_bytes = stat.rx_bytes
            rx_errors = stat.rx_errors
            tx_packets = stat.tx_packets
            tx_bytes = stat.tx_bytes
            tx_errors = stat.tx_errors
            
            # Store information in dictionary
            self.port_stats[dpid][port_no] = {
                'rx_packets': rx_packets,
                'rx_bytes': rx_bytes,
                'rx_errors': rx_errors,
                'tx_packets': tx_packets,
                'tx_bytes': tx_bytes,
                'tx_errors': tx_errors,
                'timestamp': time.time()
            }
            
            # Calculate bandwidth if previous data exists
            if port_no in self.port_stats.get(dpid, {}):
                old_stats = self.port_stats[dpid][port_no]
                time_diff = self.port_stats[dpid][port_no]['timestamp'] - old_stats.get('timestamp', 0)
                
                if time_diff > 0:
                    rx_bps = (rx_bytes - old_stats.get('rx_bytes', 0)) * 8 / time_diff
                    tx_bps = (tx_bytes - old_stats.get('tx_bytes', 0)) * 8 / time_diff
                    
                    # Display bandwidth
                    self.logger.info("Bandwidth port %d: Rx: %.2f Mbps, Tx: %.2f Mbps", 
                                     port_no, rx_bps/1000000, tx_bps/1000000)
            
            # Print port stats information
            self.logger.info("%-8d %-12d %-12d %-12d %-12d %-12d %-12d",
                             port_no, rx_packets, rx_bytes, rx_errors, tx_packets, tx_bytes, tx_errors)

if __name__ == '__main__':
    # To run standalone, use:
    # ryu-manager network_monitor.py
    from ryu.cmd import manager
    manager.main()