import sys
import os

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
sys.path.insert(0, os.path.abspath(os.path.join(FILE, f"../../../../utils/pb")))

import grpc
import logging
import utils.utils_pb2 as utils
import order_queue.order_queue_pb2 as order_queue
import order_queue.order_queue_pb2_grpc as order_queue_rpc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] - [%(levelname)s] - [Orchestrator] - [Thread %(thread)d] - %(message)s"
)

logger = logging.getLogger()

def insert_order_to_queue(request, order_id):
    with grpc.insecure_channel('order_queue:50054') as channel:
        stub = order_queue_rpc.OrderQueueServiceStub(channel)

        response: order_queue.EnqueueResponse = stub.Enqueue(order_queue.EnqueueRequest(
            order_id=order_id,
            user=utils.User(
                name=request["user"]["name"],
                contact=request["user"]["contact"],
                address=utils.Address(
                    street=request["billingAddress"]["street"],
                    city=request["billingAddress"]["city"],
                    state=request["billingAddress"]["state"],
                    zip=request["billingAddress"]["zip"],
                    country=request["billingAddress"]["country"]
                )
            ),
            items=[utils.Item(name=item["name"], quantity=item["quantity"]) for item in request["items"]]
        ))

        if not response.success:
            raise Exception(order_id, "Order queue: failed to enqueue order")
        
        logger.info(f"[Order {order_id}] - Order enqueued successfully")
