# week04-udp-multicast-basic/receiver.py
import socket
import struct
import threading
import time
from config import CHANNELS, PORT, BUFFER_SIZE

class DynamicReceiver:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("", PORT))
        self.active_memberships = {} # name -> mreq
        self.running = True

    def join_group(self, name):
        name = name.lower()
        if name not in CHANNELS:
            print(f"!! Unknown channel: {name}")
            return
        if name in self.active_memberships:
            print(f"!! Already joined {name}")
            return

        group = CHANNELS[name]
        mreq = struct.pack("4sl", socket.inet_aton(group), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.active_memberships[name] = mreq
        print(f">> Joined {name} ({group})")

    def leave_group(self, name):
        name = name.lower()
        if name not in self.active_memberships:
            print(f"!! Not a member of {name}")
            return

        mreq = self.active_memberships[name]
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
        del self.active_memberships[name]
        print(f"<< Left {name}")

    def listen_loop(self):
        self.sock.settimeout(1.0)
        while self.running:
            try:
                data, addr = self.sock.recvfrom(BUFFER_SIZE)
                print(f"\n[RCV] From {addr}: {data.decode()}")
                print("Cmd (join/leave <name>, list, exit): ", end="", flush=True)
            except socket.timeout:
                continue
            except Exception as e:
                if self.running: print(f"\n!! Socket error: {e}")
                break

    def start(self):
        threading.Thread(target=self.listen_loop, daemon=True).start()
        print("--- Dynamic Multicast Receiver ---")
        print(f"Available: {', '.join(CHANNELS.keys())}")
        print("Commands: join <name>, leave <name>, list, exit")
        
        while self.running:
            try:
                cmd_line = input("Cmd (join/leave <name>, list, exit): ").strip().split()
                if not cmd_line: continue
                
                action = cmd_line[0].lower()
                
                if action == "exit":
                    self.running = False
                elif action == "list":
                    print(f"Active: {', '.join(self.active_memberships.keys()) if self.active_memberships else 'None'}")
                elif action == "join" and len(cmd_line) > 1:
                    self.join_group(cmd_line[1])
                elif action == "leave" and len(cmd_line) > 1:
                    self.leave_group(cmd_line[1])
                else:
                    print("!! Invalid command.")
            except EOFError:
                break
        
        print("Shutting down...")
        self.sock.close()

if __name__ == "__main__":
    DynamicReceiver().start()
