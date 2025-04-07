import sys
import os

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
order_executor_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb'))
sys.path.insert(0, order_executor_grpc_path)
from order_queue.order_queue_pb2 import *
from order_queue.order_queue_pb2_grpc import *
from order_executor.order_executor_pb2 import *
from order_executor.order_executor_pb2_grpc import *

import time
import grpc
import socket
import random
import hashlib
import logging
import threading
from concurrent import futures
from google.protobuf import empty_pb2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] - [%(levelname)s] - [Order Executor] - [Thread %(thread)d] - %(message)s"
)

logger = logging.getLogger()

def get_hash(value):
    return int(hashlib.sha256(value.encode()).hexdigest(), 16) & 0xFFFFFFFF

class OrderExecutorService(OrderExecutorServiceServicer):
    def __init__(self):
        # Derive the ID from IP address
        own_ip = socket.gethostbyname(socket.gethostname())
        self.id_ip = (get_hash(own_ip), own_ip)
        self.peers = []

        logger.info(f"Order executor service initialized with ID: {self.id_ip[0]}")

        # Set current leader to None
        self.leader = None
        self.leader_lock = threading.RLock()
        self.leader_election = False
        self.leader_election_lock = threading.RLock()

        # Schedule order execution
        threading.Thread(target=self.run, daemon=True).start()

        # Schedule leader monitoring after a short delay
        monitor_thread = threading.Timer(1 + 10 * random.random(), self.monitor_leader)
        monitor_thread.daemon = True
        monitor_thread.start()

    def discover_peers(self):
        # Get list of all peers in the cluster
        peer_ips = socket.gethostbyname_ex("order_executor")[2]

        # Filter out the current IP address
        self.peers = [(get_hash(ip), ip) for ip in peer_ips if ip != self.id_ip[1]]
        logger.debug(f"Discovered peers: {self.peers}")

    def is_peer_known(self, peer):
        return any(peer == p[1] for p in self.peers)

    def declare_leadership(self):
        if self.leader is not None:
            return
            
        time.sleep(1.5) # Wait a bit to avoid redundant elections

        with self.leader_election_lock:
            # If election already concluded in another thread, return
            if not self.leader_election:
                return
            
            with self.leader_lock:
                self.leader_election = False
                self.leader = (self.id_ip[0], self.id_ip[1])
                logger.info(f"I am the new leader: {self.leader[0]}")

        def send_coordinator_message(peer):
            try:
                with grpc.insecure_channel(f"{peer[1]}:50055") as channel:
                    stub = OrderExecutorServiceStub(channel)
                    stub.Coordinator(empty_pb2.Empty(), timeout=3)
            except grpc.RpcError:
                logger.error(f"Failed to send coordinator message to {peer[0]}")
                self.peers.remove(peer)

        # Notify all peers about the new leader
        with futures.ThreadPoolExecutor() as executor:
            executor.map(send_coordinator_message, self.peers)

    def start_leader_election(self):
        self.leader_election = True
        self.discover_peers()

        if self.leader is not None:
            return

        # Send election request to all peers with higher IDs
        peers = [peer for peer in self.peers if peer[0] > self.id_ip[0]]
        responses = 0

        def send_election_request(peer):
            nonlocal responses

            try:
                with grpc.insecure_channel(f"{peer[1]}:50055") as channel:
                    stub = OrderExecutorServiceStub(channel)
                    response: ExecutorResponse = stub.Election(empty_pb2.Empty(), timeout=3)

                    if not response.ok:
                        raise grpc.RpcError()

                    responses += 1
            except grpc.RpcError:
                logger.error(f"Failed to send election request to {peer[0]}")
                self.peers.remove(peer)

        # Use ThreadPoolExecutor to send election requests concurrently
        with futures.ThreadPoolExecutor() as executor:
            executor.map(send_election_request, peers)

        # If no peers responded, I am the leader
        if responses == 0:
            self.declare_leadership()

    def monitor_leader(self):
        while True:
            with self.leader_lock, self.leader_election_lock:
                leader_election = self.leader_election
                leader = self.leader

            if leader_election:
                time.sleep(5)
                continue

            elif leader is None:
                logger.warning("No leader found - starting leader election")
                self.start_leader_election()

            elif leader[0] != self.id_ip[0]:
                # Check if the leader is alive
                try:
                    with grpc.insecure_channel(f"{leader[1]}:50055") as channel:
                        stub = OrderExecutorServiceStub(channel)
                        response: ExecutorResponse = stub.Ping(empty_pb2.Empty(), timeout=3)

                        if not response.ok:
                            raise grpc.RpcError()
                except grpc.RpcError:
                    logger.warning(f"Leader {leader[0]} is down - starting leader election")

                    with self.leader_lock:
                        self.leader = None

                    self.start_leader_election()

            # Sleep for a while before checking again
            time.sleep(5)
        
    def Ping(self, _: empty_pb2.Empty, context):
        peer = context.peer().lstrip('ipv4:').split(':')[0]
        logger.debug(f"Received ping from {get_hash(peer)}")

        if not self.is_peer_known(peer):
            self.discover_peers()

        return ExecutorResponse(ok=True)

    def Election(self, _: empty_pb2.Empty, context):
        peer = context.peer().lstrip('ipv4:').split(':')[0]
        logger.debug(f"Received election request from {get_hash(peer)}")

        with self.leader_lock:
            self.leader = None

        if not self.is_peer_known(peer):
            self.discover_peers()

        # Continue the leader election process
        with self.leader_election_lock:
            if not self.leader_election:
                logger.debug(f"Continuing leader election...")
                threading.Thread(target=self.start_leader_election, daemon=True).start()

        return ExecutorResponse(ok=True)

    def Coordinator(self, _: empty_pb2.Empty, context):
        peer = context.peer().lstrip('ipv4:').split(':')[0]
        logger.debug(f"Received coordinator request from {get_hash(peer)}")

        with self.leader_lock, self.leader_election_lock:
            self.leader = (get_hash(peer), peer)
            self.leader_election = False
            logger.info(f"New leader elected: {self.leader[0]}")

        if not self.is_peer_known(peer):
            self.discover_peers()

        return empty_pb2.Empty()

    def run(self):
        while True:
            # If I'm the leader, execute orders
            if not self.leader_election and self.leader and self.leader[0] == self.id_ip[0]:
                with grpc.insecure_channel("order_queue:50054") as channel:
                    stub = OrderQueueServiceStub(channel)
                    response: DequeueResponse = stub.Dequeue(empty_pb2.Empty())

                    if response.order_id and response.order_id != "":
                        # Simulate order execution
                        logger.info(f"[Order {response.order_id}] - Order is being executed...")

                        # After executing continue to next order
                        continue

            # If I'm not the leader or no orders were found, sleep for a while before checking again
            time.sleep(5)

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add the order executor service to the server
    add_OrderExecutorServiceServicer_to_server(OrderExecutorService(), server)
    # Listen on port 50055
    port = "50055"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    logger.info("Server started. Listening on port 50055.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
