# week08-opportunistic-advanced/node/bundle_manager.py
import os
import json
import hashlib

class BundleManager:
    """Manages 'bundles' (grouped data chunks) for opportunistic sharing."""
    def __init__(self, node_id, storage_dir):
        self.node_id = node_id
        self.storage_dir = storage_dir
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
        self.bundles = self._load()

    def create_bundle(self, content, source_app, priority=3):
        bundle_id = hashlib.sha1(f"{self.node_id}_{os.urandom(8)}".encode()).hexdigest()[:12]
        bundle = {
            "id": bundle_id,
            "source": self.node_id,
            "app": source_app,
            "content": content,
            "priority": priority,
            "hops": 0,
            "timestamp": os.path.getmtime(__file__) if os.path.exists(__file__) else 0
        }
        self.bundles[bundle_id] = bundle
        self._save()
        return bundle_id

    def get_bundle(self, bid):
        return self.bundles.get(bid)

    def integrate_bundle(self, bundle):
        bid = bundle['id']
        if bid not in self.bundles:
            # Check priority/storage limits here in a real app
            self.bundles[bid] = bundle
            self._save()
            return True
        return False

    def get_catalog(self):
        """Returns summarized metadata for all bundles."""
        return {bid: {"priority": b['priority'], "hops": b['hops']} for bid, b in self.bundles.items()}

    def _save(self):
        path = os.path.join(self.storage_dir, f"catalog_{self.node_id}.json")
        with open(path, 'w') as f:
            json.dump(self.bundles, f, indent=2)

    def _load(self):
        path = os.path.join(self.storage_dir, f"catalog_{self.node_id}.json")
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except: pass
        return {}
