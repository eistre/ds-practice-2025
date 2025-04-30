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
from leader_election_service import LeaderElectionService
from utils.utils_pb2_grpc import add_LeaderElectionServiceServicer_to_server

import time
import grpc
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

class OrderExecutorService(LeaderElectionService):
    def __init__(self):
        super().__init__(service_name="order_executor", port="50055", logger=logger)
        logger.info(f"Order executor service initialized with ID: {self.id_ip[0]}")

        # Schedule order execution
        threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        while True:
            # If I'm the leader, execute orders
            if not self.ongoing_election and self.leader and self.leader[0] == self.id_ip[0]:
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
    add_LeaderElectionServiceServicer_to_server(OrderExecutorService(), server)
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
