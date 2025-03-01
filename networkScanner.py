import pyshark

# Live capture from a specific interface
def live_capture():
    # Replace 'eth0' with your network interface
    capture = pyshark.LiveCapture(interface='eth0')
    capture.sniff(timeout=10)  # Capture for 10 seconds
    
    for packet in capture:
        print(packet)

# Read from a capture file
def read_pcap(file_path):
    capture = pyshark.FileCapture(file_path)
    for packet in capture:
        print(packet)

# Filter packets (example: only TCP packets)
def filtered_capture():
    capture = pyshark.LiveCapture(interface='eth0', display_filter='tcp')
    capture.sniff(timeout=10)
    
    for packet in capture:
        # Access specific fields
        if hasattr(packet, 'ip'):
            print(f"Source IP: {packet.ip.src}, Destination IP: {packet.ip.dst}")
