import time
import random
import socket
import hashlib
import logging
import threading
from concurrent import futures
from google.protobuf import empty_pb2
from utils.utils_pb2 import *
from utils.utils_pb2_grpc import *

def get_hash(value: str):
    return int(hashlib.sha256(value.encode()).hexdigest(), 16) & 0xFFFFFFFF

class LeaderElectionService(LeaderElectionServiceServicer):
    def __init__(self, service_name: str, port: str, logger: logging.Logger):
        # Derive the ID from IP address
        own_ip = socket.gethostbyname(socket.gethostname())
        
        # Initialize the service with its ID and IP address
        self.peers = {}
        self.id_ip = (get_hash(own_ip), own_ip)
        self.port = port
        self.service_name = service_name

        # Set current leader to None
        self.leader = None
        self.ongoing_election = False
        self.lock = threading.RLock()

        # Initialize monitoring
        self.monitor_event = threading.Event()
        threading.Thread(target=self.monitor_leader, daemon=True).start()

        # Initialize logger
        self.logger = logger

        # Schedule leader election
        election_thread = threading.Timer(1.5, self.start_leader_election)
        election_thread.daemon = True
        election_thread.start()

    def discover_peers(self):
        # Get list of all peers in the cluster
        peer_ips = socket.gethostbyname_ex(self.service_name)[2]

        # Filter out the current IP address
        self.peers = {get_hash(ip): ip for ip in peer_ips if ip != self.id_ip[1]}

    def stop_election(self):
        time.sleep(1) # Wait a bit to avoid redundant elections
        self.monitor_event.set()
        self.ongoing_election = False

    def declare_leadership(self):
        with self.lock:
            if self.leader is not None:
                self.logger.debug("Leader already elected")
                return

            # Declare self as the leader
            self.leader = self.id_ip
            self.logger.info(f"I am the new leader: {self.leader}")

            def send_coordinator_message(peer):
                try:
                    with grpc.insecure_channel(f"{peer[1]}:{self.port}") as channel:
                        stub = LeaderElectionServiceStub(channel)
                        stub.Coordinator(empty_pb2.Empty())
                except Exception:
                    self.logger.warning(f"Failed to send coordinator message to {peer}")
                    del self.peers[peer[0]]

            # Send coordinator message to all peers
            with futures.ThreadPoolExecutor() as executor:
                executor.map(send_coordinator_message, [peer for peer in self.peers.items()])
            
            # Stop the election process after a short delay
            threading.Thread(target=self.stop_election, daemon=True).start()

    def start_leader_election(self):
        with self.lock:
            if self.leader is not None:
                self.logger.debug("Leader already elected - skipping election")
                return
            
            # Set election in progress
            self.ongoing_election = True
            
            # Discover peers
            self.discover_peers()

            # Send election requests to all peers with higher IDs
            peers = [peer for peer in self.peers.items() if peer[0] > self.id_ip[0]]
            self.logger.debug(f"Peers with higher IDs: {peers}")

            if len(peers) == 0:
                # No peers with higher IDs, declare self as leader
                self.declare_leadership()
                return

            def send_election_request(peer):
                try:
                    with grpc.insecure_channel(f"{peer[1]}:{self.port}") as channel:
                        stub = LeaderElectionServiceStub(channel)
                        response: ElectionResponse = stub.Election(empty_pb2.Empty())

                        if not response.ok:
                            raise grpc.RpcError()
                        
                        return 1
                                            
                except Exception:
                    self.logger.warning(f"Failed to send election request to {peer}")
                    del self.peers[peer[0]]

                    return 0

            # Use ThreadPoolExecutor to send requests concurrently
            with futures.ThreadPoolExecutor() as executor:
                responses = executor.map(send_election_request, peers)

            # If no responses received, declare self as leader
            if sum(responses) == 0:
                self.declare_leadership()

    def monitor_leader(self):
        time.sleep(1 + random.uniform(0, 5)) # Random delay to spread out the start of monitoring
        self.logger.debug("Starting leader monitoring")

        # Periodically check if the leader is alive
        while True:
            time.sleep(5) # Check every 5 seconds

            if not self.monitor_event.is_set():
                self.monitor_event.wait() # Block until ongoing election is complete
                continue

            leader = self.leader

            if not self.ongoing_election and leader is None:
                self.logger.info("No leader found - starting leader election")
                self.monitor_event.clear()
                threading.Thread(target=self.start_leader_election, daemon=True).start()
            elif leader[0] != self.id_ip[0]:
                # Check if the leader is alive
                try:
                    with grpc.insecure_channel(f"{leader[1]}:{self.port}") as channel:
                        stub = LeaderElectionServiceStub(channel)
                        stub.Ping(empty_pb2.Empty(), timeout=3)
                except Exception:
                    if self.ongoing_election or self.leader[0] != leader[0]:
                        continue  # Ignore if an election is in progress or if the leader has changed

                    self.logger.warning(f"Leader {leader} is down - starting leader election")

                    # Set election in progress
                    self.leader = None
                    self.monitor_event.clear()
                    threading.Thread(target=self.start_leader_election, daemon=True).start()

    def Ping(self, _, context):
        peer = context.peer().lstrip("ipv4:").split(":")[0]
        self.logger.debug(f"Received ping from {get_hash(peer)}")
        return PingResponse(ok=True)

    def Election(self, _, context):
        peer = context.peer().lstrip("ipv4:").split(":")[0]
        self.logger.debug(f"Received election request from {get_hash(peer)}")

        if self.ongoing_election:
            self.logger.debug("Election already in progress - avoiding duplicate requests")
            return ElectionResponse(ok=True)
        
        # Set election in progress
        self.leader = None
        self.monitor_event.clear()

        # Continue the election process
        self.logger.debug("Continuing election process...")
        threading.Thread(target=self.start_leader_election, daemon=True).start()

        return ElectionResponse(ok=True)

    def Coordinator(self, _, context):
        peer = context.peer().lstrip("ipv4:").split(":")[0]
        self.logger.debug(f"Received coordinator request from {get_hash(peer)}")

        # Stop the election process after a short delay
        self.ongoing_election = True
        self.monitor_event.clear()
        threading.Thread(target=self.stop_election, daemon=True).start()

        self.leader = (get_hash(peer), peer)
        self.logger.info(f"New leader elected: {self.leader}")        

        return empty_pb2.Empty()
