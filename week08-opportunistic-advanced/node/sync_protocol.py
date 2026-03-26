# week08-opportunistic-advanced/node/sync_protocol.py
import json

class SyncProtocol:
    """Handles the 3-way handshake logic for opportunistic mesh sync."""
    
    @staticmethod
    def create_hello(node_id, catalog):
        return {"type": "HELLO", "node": node_id, "catalog": catalog}

    @staticmethod
    def compare_catalogs(my_catalog, peer_catalog):
        """Identifies what we need from them and what they need from us."""
        my_ids = set(my_catalog.keys())
        peer_ids = set(peer_catalog.keys())
        
        needed_by_me = list(peer_ids - my_ids)
        needed_by_them = list(my_ids - peer_ids)
        
        # Priority check: Sort by priority (if provided in catalog)
        needed_by_me.sort(key=lambda bid: peer_catalog[bid].get('priority', 0), reverse=True)
        return needed_by_me, needed_by_them

    @staticmethod
    def create_request(node_id, needed_ids):
        return {"type": "PULL", "node": node_id, "wanted": needed_ids}

    @staticmethod
    def create_data_packet(node_id, bundle):
        return {"type": "DATA", "node": node_id, "bundle": bundle}
