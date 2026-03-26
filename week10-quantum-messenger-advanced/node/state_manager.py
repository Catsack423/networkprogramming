# week10-quantum-messenger-advanced/node/state_manager.py
import time
import random

class QuantumStateManager:
    def __init__(self, node_id, token_lifespan, collapse_prob, logger):
        self.node_id = node_id
        self.lifespan = token_lifespan
        self.collapse_prob = collapse_prob
        self.logger = logger
        self.active_tokens = {} # token_id -> Token Object
        self.history = set()    # Prevent loop back of read/collapsed tokens

    def ingest_token(self, token):
        """Processes an incoming token. Decides if it should collapse due to environment."""
        if token.id in self.history:
            self.logger.log_state_change(token.id, "REJECTED", "Already processed this quantum state")
            return False

        valid, reason = token.is_valid()
        if not valid:
            self.logger.log_state_change(token.id, "COLLAPSED_ON_ARRIVAL", reason)
            return False

        # Simulate environmental interference collapsing the state occasionally
        if random.random() < self.collapse_prob:
            token._corrupt()
            self.logger.log_state_change(token.id, "ENVIRONMENTAL_COLLAPSE", "Interference during transit")
            self.history.add(token.id)
            return False

        self.active_tokens[token.id] = token
        self.history.add(token.id)
        self.logger.log_state_change(token.id, "INGESTED", "State coherent")
        return True

    def attempt_read(self, token_id):
        """Attempt to read a state if it reached its target node."""
        if token_id not in self.active_tokens:
            return None, "STATE_UNAVAILABLE"
            
        token = self.active_tokens[token_id]
        payload, status = token.read_payload()
        
        # Once read/collapsed, it is removed from active pool
        del self.active_tokens[token_id]
        
        if payload:
            self.logger.log_state_change(token_id, "SUCCESSFUL_READ", f"Payload secured")
        else:
            self.logger.log_state_change(token_id, "FAILED_READ", status)
        
        return payload, status

    def get_forwardable_tokens(self, max_hops):
        """Returns tokens that are still coherent and haven't exceeded hop limits."""
        forwardable = []
        now = time.time()
        
        for tid, token in list(self.active_tokens.items()):
            valid, _ = token.is_valid()
            if not valid or (now - token.birth > token.lifespan):
                self.logger.log_state_change(token.id, "DECAYED_IN_QUEUE", "Lifespan exceeded")
                del self.active_tokens[token_id]
            elif token.hops >= max_hops:
                self.logger.log_state_change(token.id, "HOP_LIMIT_EXCEEDED", "State degraded")
                token._corrupt()
                del self.active_tokens[token_id]
            else:
                forwardable.append(token)
                
        return forwardable

    def remove_token(self, token_id):
        """Used when a token is successfully forwarded (No-Cloning)."""
        if token_id in self.active_tokens:
            del self.active_tokens[token_id]
            self.logger.log_state_change(token_id, "FORWARDED", "Local state destroyed")
