import psutil
from byteConverter import get_size

def printNetwork():
    print("=" * 40, "Network Information", "=" * 40)
    # get all network interfaces (virtual and physical)

    for interface_name, interface_addresses in getAllNetworkInterfaces().items():
        for address in interface_addresses:
            print(f"=== Interface: {interface_name} ===")

            if str(address.family) == "AddressFamily.AF_INET":
                print(f"  IP Address: {address.address}")
                print(f"  Netmask: {address.netmask}")
                print(f"  Broadcast IP: {address.broadcast}")

            elif str(address.family) == "AddressFamily.AF_PACKET":
                print(f"  MAC Address: {address.address}")
                print(f"  Netmask: {address.netmask}")
                print(f"  Broadcast MAC: {address.broadcast}")

    # get IO statistics since boot
    net_io = psutil.net_io_counters()
    print(f"Total Bytes Sent: {get_size(net_io.bytes_sent)}")
    print(f"Total Bytes Received: {get_size(net_io.bytes_recv)} \n")

def getAllNetworkInterfaces():
    return psutil.net_if_addrs()