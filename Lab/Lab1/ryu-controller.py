from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types


class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.switches = {}
        self.logger.info("Ryu controller started!")

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        # Lưu thông tin về switch
        self.switches[datapath.id] = datapath
        
        # Log khi switch kết nối
        self.logger.info("Switch %s connected to controller", datapath.id)

        # Cài đặt table-miss flow entry
        # Khi không có flow entry nào khớp, gửi gói tin đến controller
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                         ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Tạo flow mod message với các instruction
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                            actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                   priority=priority, match=match,
                                   instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                   match=match, instructions=inst)
            
        # Gửi flow mod message đến switch
        datapath.send_msg(mod)
        self.logger.info("Flow added to switch %s: match=%s, actions=%s, priority=%s", 
                        datapath.id, match, actions, priority)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # Xử lý khi nhận được packet in message từ switch
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        # Phân tích gói tin
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        # Bỏ qua các gói tin LLDP
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return
            
        # Lấy địa chỉ MAC nguồn và đích
        dst = eth.dst
        src = eth.src

        # ID của datapath (switch)
        dpid = datapath.id
        
        # Khởi tạo từ điển cho switch nếu chưa tồn tại
        self.mac_to_port.setdefault(dpid, {})

        # Log các thông tin về gói tin
        self.logger.info("PacketIn: switch=%s src=%s dst=%s in_port=%s", 
                        dpid, src, dst, in_port)

        # Học địa chỉ MAC nguồn và cổng vào
        self.mac_to_port[dpid][src] = in_port

        # Xác định cổng ra dựa trên địa chỉ MAC đích
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            # Nếu không biết địa chỉ MAC đích, flood gói tin
            out_port = ofproto.OFPP_FLOOD

        # Xác định hành động cho gói tin
        actions = [parser.OFPActionOutput(out_port)]

        # Nếu không phải flood, thêm flow entry mới
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            
            # Nếu gói tin đang được buffer trên switch
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                return
            else:
                self.add_flow(datapath, 1, match, actions)
                
        # Xử lý dữ liệu gói tin
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        # Gửi gói tin ra cổng tương ứng
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)
        self.logger.info("PacketOut: switch=%s in_port=%s actions=%s", 
                        dpid, in_port, actions)