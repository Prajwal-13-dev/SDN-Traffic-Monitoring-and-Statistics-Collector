from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr

log = core.getLogger()

class OrangeFirewall(object):
    def __init__(self, connection):
        self.connection = connection
        # Listen to the switch connection for events
        connection.addListeners(self)

    def _handle_PacketIn(self, event):
        """
        Handles packet_in events from the switches.
        """
        packet = event.parsed
        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return

        # Look for an IPv4 packet inside the frame
        ip_packet = packet.find('ipv4')
        
        if ip_packet is not None:
            # --- ORANGE PROBLEM SPECIFIC LOGIC: FIREWALL / FILTERING ---
            # Block traffic between h1 (10.0.0.1) and h4 (10.0.0.4)
            if (ip_packet.srcip == IPAddr("10.0.0.1") and ip_packet.dstip == IPAddr("10.0.0.4")) or \
               (ip_packet.srcip == IPAddr("10.0.0.4") and ip_packet.dstip == IPAddr("10.0.0.1")):
                
                log.info("BLOCKED traffic between %s and %s" % (ip_packet.srcip, ip_packet.dstip))
                
                # Create an OpenFlow flow modification message (match+action logic)
                msg = of.ofp_flow_mod()
                msg.match = of.ofp_match.from_packet(packet)
                msg.idle_timeout = 30
                msg.hard_timeout = 30
                msg.priority = 100
                
                # Because we do NOT add any actions to msg.actions, the switch will DROP the packet.
                self.connection.send(msg)
                
                # Halt the event so the learning switch component below doesn't forward it!
                return event.halt 
                
        # If it's not our blocked traffic, do nothing and let the Learning Switch handle it.
        return 

def launch():
    """
    Starts the component.
    """
    def start_switch(event):
        log.info("Controlling %s" % (event.connection,))
        OrangeFirewall(event.connection)
    
    # Listen for switches connecting to our controller
    core.openflow.addListenerByName("ConnectionUp", start_switch)
    
    # Also launch POX's built-in L2 learning switch. 
    # This handles the "Allowed" traffic automatically.
    from pox.forwarding.l2_learning import launch as l2_launch
    l2_launch()
