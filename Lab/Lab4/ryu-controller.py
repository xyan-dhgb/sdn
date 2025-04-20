#!/usr/bin/env python3

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
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
        self.stats_interval = 10  # Thời gian gửi request stats (giây)

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.debug('Datapath registered: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('Datapath unregistered: %016x', datapath.id)
                del self.datapaths[datapath.id]

    def _monitor(self):
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(self.stats_interval)

    def _request_stats(self, datapath):
        self.logger.debug('Sending stats request to datapath: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Gửi Flow Statistics Request
        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

        # Gửi Port Statistics Request
        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Cài đặt bảng chuyển tiếp mặc định với rule để gửi các gói tin không khớp lên controller
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None, idle_timeout=0, hard_timeout=0):
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
        # Nếu không có switch kết nối, thì không làm gì
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("Packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # Bỏ qua gói tin LLDP
            return
        
        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        self.logger.info("Packet in %s %s %s %s", dpid, src, dst, in_port)

        # Học địa chỉ MAC đến port
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # Cài đặt flow để tránh gửi gói tin lên controller trong tương lai
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            # Đặt timeout cho các flow entry để có thể cập nhật khi topology thay đổi
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 1, match, actions, msg.buffer_id, idle_timeout=20, hard_timeout=60)
                return
            else:
                self.add_flow(datapath, 1, match, actions, idle_timeout=20, hard_timeout=60)

        # Gửi gói tin ra cổng tương ứng
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        """Xử lý phản hồi về Flow Statistics từ switch"""
        body = ev.msg.body
        
        self.logger.info('=== Flow Stats Reply from Switch %016x ===', ev.msg.datapath.id)
        self.logger.info('datapath         '
                         'in-port  eth-dst           '
                         'out-port packets  bytes    ')
        self.logger.info('---------------- '
                         '-------- ----------------- '
                         '-------- -------- --------')

        for stat in sorted([flow for flow in body if flow.priority == 1],
                           key=lambda flow: (flow.match['in_port'],
                                             flow.match.get('eth_dst', "00:00:00:00:00:00"))):
            try:
                self.logger.info('%016x %8x %17s %8x %8d %8d',
                                 ev.msg.datapath.id,
                                 stat.match['in_port'], stat.match.get('eth_dst', "00:00:00:00:00:00"),
                                 stat.instructions[0].actions[0].port,
                                 stat.packet_count, stat.byte_count)
            except:
                pass

    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        """Xử lý phản hồi về Port Statistics từ switch"""
        body = ev.msg.body

        self.logger.info('=== Port Stats Reply from Switch %016x ===', ev.msg.datapath.id)
        self.logger.info('port     rx-packets rx-bytes  rx-errors '
                         'tx-packets tx-bytes  tx-errors')
        self.logger.info('-------- ---------- --------- --------- '
                         '---------- --------- ---------')
        
        for stat in sorted(body, key=attrgetter('port_no')):
            self.logger.info('%8x %10d %9d %9d %10d %9d %9d',
                              stat.port_no,
                              stat.rx_packets, stat.rx_bytes, stat.rx_errors,
                              stat.tx_packets, stat.tx_bytes, stat.tx_errors)

if __name__ == '__main__':
    from ryu.cmd import manager
    manager.main()