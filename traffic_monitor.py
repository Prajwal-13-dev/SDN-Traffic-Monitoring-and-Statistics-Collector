from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.recoco import Timer
import datetime

log = core.getLogger()

class TrafficMonitor(object):
    def __init__(self, connection):
        self.connection = connection
        # Listen for events from the switch
        connection.addListeners(self)
        
        # Start a background timer that fires every 10 seconds
        log.info("Starting Traffic Monitor for Switch %s", connection.dpid)
        Timer(10, self._request_stats, recurring=True)

    def _request_stats(self):
        """
        Periodic function to ask the switch for its flow statistics.
        """
        # Create an OpenFlow stats request message
        msg = of.ofp_stats_request(body=of.ofp_flow_stats_request())
        self.connection.send(msg)
        log.debug("Requested stats from switch %s", self.connection.dpid)

    def _handle_FlowStatsReceived(self, event):
        """
        Triggered when the switch replies with the packet/byte counts.
        """
        stats = event.stats
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report_lines = []
        report_lines.append(f"--- Traffic Report: Switch {event.connection.dpid} @ {timestamp} ---")
        
        # Iterate through every flow rule currently on the switch
        for flow in stats:
            # We ignore completely empty rules to keep the report clean
            if flow.packet_count > 0:
                line = f"Match: {flow.match} | Packets: {flow.packet_count} | Bytes: {flow.byte_count}"
                report_lines.append(line)
                log.info(line) # Print to terminal
                
        report_lines.append("---------------------------------------------------\n")
        
        # Write the data to a text file to generate a "Simple Report"
        with open("traffic_report.txt", "a") as file:
            file.write("\n".join(report_lines) + "\n")

def launch():
    """
    Starts the component.
    """
    def start_switch(event):
        TrafficMonitor(event.connection)
    
    # Listen for switches connecting to our controller
    core.openflow.addListenerByName("ConnectionUp", start_switch)
    
    # Launch the standard L2 learning switch so pings actually work
    from pox.forwarding.l2_learning import launch as l2_launch
    l2_launch()
