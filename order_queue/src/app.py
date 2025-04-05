import sys
import os

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
order_queue_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb'))
sys.path.insert(0, order_queue_grpc_path)
from utils.utils_pb2 import *
from order_queue.order_queue_pb2 import *
from order_queue.order_queue_pb2_grpc import *

import grpc
import logging
import threading
from concurrent import futures
from queue import PriorityQueue
from google.protobuf import empty_pb2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] - [%(levelname)s] - [Order Queue] - [Thread %(thread)d] - %(message)s"
)

logger = logging.getLogger()

# Class for order queue
class OrderQueueService(OrderQueueServiceServicer):
    def __init__(self):
        self._lock = threading.Lock()
        self._queue = PriorityQueue()
        logger.info("Order queue service initialized")

    def _generate_priority(self, request: EnqueueRequest):
        request_unique_string = f"""
            {request.order_id}
            {request.user.name}
            {request.user.contact}
            {request.user.address.country}
            {request.user.address.city}
            {", ".join([f'{item.name} - {item.quantity}' for item in request.items])}
        """

        # Use the hash of the request unique string as the priority
        return hash(request_unique_string)

    def Enqueue(self, request: EnqueueRequest, _):
        with self._lock:
            # Check if the order already exists in the queue
            if any(order_id == request.order_id for _, order_id in self._queue.queue):
                logger.error(f"[Order {request.order_id}] - Order already exists in the queue")
                return EnqueueResponse(success=False)

            # Generate the priority for the request
            request_priority = self._generate_priority(request)

            # Put the order in the queue
            self._queue.put((request_priority, request.order_id))
            logger.info(f"[Order {request.order_id}] - Order enqueued")

            return EnqueueResponse(success=True)
    
    def Dequeue(self, request: empty_pb2.Empty, _):
        with self._lock:
            # Check if the queue is empty
            if self._queue.empty():
                return DequeueResponse(order_id="")
        
            # Pop the order with the highest priority
            order_id = self._queue.get()
            logger.info(f"[Order {order_id[1]}] - Order dequeued")

            return DequeueResponse(order_id=order_id[1])
    
def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add the order queue service to the server
    add_OrderQueueServiceServicer_to_server(OrderQueueService(), server)
    # Listen on port 50054
    port = "50054"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    logger.info("Server started. Listening on port 50054.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
