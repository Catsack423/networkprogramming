"""
subnet.py — Subnet Broadcast Address Utility
Auto-detects the host's local IP and subnet mask, then computes the
subnet-specific broadcast address using bitwise AND/OR.

Why subnet broadcast instead of 255.255.255.255?
  255.255.255.255 (limited broadcast) never leaves the local host's socket layer
  on some OSes/routers.  The subnet broadcast (e.g. 192.168.1.255) is directed
  and more compatible with modern network stacks.
"""

import socket
import struct
import platform


def _get_local_ip() -> str:
    """Determine the primary outbound IP by connecting a UDP socket (no data sent)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))   # Google DNS — just for routing decision
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def _get_subnet_mask_windows(local_ip: str) -> str:
    """Use socket.getadaptersinfo equivalent via ipconfig parsing on Windows."""
    import subprocess, re
    try:
        out = subprocess.check_output("ipconfig", encoding="utf-8", errors="ignore")
        # Walk through adapter blocks and find the one matching local_ip
        blocks = re.split(r"\r?\n\r?\n", out)
        for block in blocks:
            if local_ip in block:
                m = re.search(r"Subnet Mask[\s.:]+(\d+\.\d+\.\d+\.\d+)", block)
                if m:
                    return m.group(1)
    except Exception:
        pass
    return "255.255.255.0"   # fallback assumption


def _get_subnet_mask_unix(local_ip: str) -> str:
    """Use netifaces or ifconfig to get subnet mask on Linux/macOS."""
    try:
        import netifaces
        for iface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(iface).get(netifaces.AF_INET, [])
            for a in addrs:
                if a.get("addr") == local_ip:
                    return a.get("netmask", "255.255.255.0")
    except ImportError:
        pass

    import subprocess, re
    try:
        out = subprocess.check_output(["ifconfig"], encoding="utf-8", errors="ignore")
        # Find block containing local_ip
        for block in re.split(r"\n(?=\S)", out):
            if local_ip in block:
                m = re.search(r"netmask\s+(0x[0-9a-fA-F]+|\d+\.\d+\.\d+\.\d+)", block)
                if m:
                    val = m.group(1)
                    if val.startswith("0x"):   # hex form (macOS)
                        n = int(val, 16)
                        return socket.inet_ntoa(struct.pack("!I", n))
                    return val
    except Exception:
        pass

    return "255.255.255.0"


def get_subnet_broadcast() -> str:
    """
    Returns the subnet-directed broadcast address for this machine.
    Example: local_ip=192.168.1.42, mask=255.255.255.0 → 192.168.1.255
    """
    local_ip = _get_local_ip()

    if platform.system() == "Windows":
        mask = _get_subnet_mask_windows(local_ip)
    else:
        mask = _get_subnet_mask_unix(local_ip)

    ip_int   = struct.unpack("!I", socket.inet_aton(local_ip))[0]
    mask_int = struct.unpack("!I", socket.inet_aton(mask))[0]

    # network_addr AND NOT mask = broadcast
    broadcast_int = (ip_int & mask_int) | (~mask_int & 0xFFFFFFFF)
    broadcast_ip  = socket.inet_ntoa(struct.pack("!I", broadcast_int))

    return local_ip, mask, broadcast_ip


if __name__ == "__main__":
    ip, mask, bcast = get_subnet_broadcast()
    print(f"Local IP         : {ip}")
    print(f"Subnet Mask      : {mask}")
    print(f"Broadcast Address: {bcast}")
    print()
    print("Difference from 255.255.255.255:")
    print("  255.255.255.255 → limited broadcast (may be blocked by some stacks)")
    print(f"  {bcast:<15}  → directed broadcast (subnet-specific, more compatible)")
