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
from books_database.books_database_pb2 import *
from books_database.books_database_pb2_grpc import *
from payment.payment_pb2 import PaymentRequest
from payment.payment_pb2_grpc import PaymentServiceStub
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

    def prepare_decrement_stock(self, book, order_id):
        with grpc.insecure_channel('books_database:50056') as channel:
            response: PrepareResponse = BooksDatabaseStub(channel).PrepareDecrementStock(WriteRequest(
                title=book.name,
                quantity=book.quantity,
                order_id=order_id
            ))

            return book.name, response.ready
        
    def two_phase_commit(self, order: DequeueResponse):
        logger.info(f"[Order {order.order_id}] - Starting 2PC")

        book_prepared = False
        payment_prepared = False

        try:
            # Phase 1: Preparation
            with grpc.insecure_channel("payment:50057") as payment_channel:
                payment_stub = PaymentServiceStub(payment_channel)

                logger.info(f"[Order {order.order_id}] - Preparing payment...")

                # First prepare each book decrement individually to use our improved PrepareDecrementStock logic
                with futures.ThreadPoolExecutor() as executor:
                    book_prep_resp = list(executor.map(
                        lambda book: self.prepare_decrement_stock(book, order.order_id),
                        order.items
                    ))
                    
                # Check if all preparations succeeded
                book_prepared = all(result[1] for result in book_prep_resp)
                if not book_prepared:
                    raise Exception("Book preparation failed - not enough stock")
                
                # Send Prepare to Payment
                payment_prep_resp = payment_stub.Prepare(PaymentRequest(
                    order_id=order.order_id,
                    amount=sum(item.quantity for item in order.items) * 5  # just a dummy amount, each book costs 5
                ))

                payment_prepared = payment_prep_resp.ready
                if not payment_prepared:
                    raise Exception("Payment preparation failed")

            # Phase 2: Commit or Abort
            # If both prepared, commit
            logger.info(f"[Order {order.order_id}] - Both services ready. COMMITTING...")

            with grpc.insecure_channel("books_database:50056") as books_channel, \
                grpc.insecure_channel("payment:50057") as payment_channel:

                # Send commit to both services
                BooksDatabaseStub(books_channel).CommitWrite(TransactionRequest(order_id=order.order_id))
                
                PaymentServiceStub(payment_channel).Commit(PaymentRequest(order_id=order.order_id))

            return True

        except Exception as e:
            logger.warning(f"[Order {order.order_id}] - ABORTING: {e}")

            # Abort both services if they were prepared
            if book_prepared:
                with grpc.insecure_channel("books_database:50056") as books_channel:
                    BooksDatabaseStub(books_channel).AbortWrite(TransactionRequest(order_id=order.order_id))

            if payment_prepared:
                with grpc.insecure_channel("payment:50057") as payment_channel:
                    PaymentServiceStub(payment_channel).Abort(PaymentRequest(order_id=order.order_id))

            return False

    def run(self):
        while True:
            # If I'm the leader, execute orders
            if not self.ongoing_election and self.leader and self.leader[0] == self.id_ip[0]:
                with grpc.insecure_channel("order_queue:50054") as channel:
                    stub = OrderQueueServiceStub(channel)
                    response: DequeueResponse = stub.Dequeue(empty_pb2.Empty())

                    if response.order_id and response.order_id != "":
                        # Simulate order execution
                        logger.info(f"[Order {response.order_id}] - Executing order...")
                        
                        #if self.execute_order(response):
                        if self.two_phase_commit(response):
                            logger.info(f"[Order {response.order_id}] - Order executed successfully")
                        else:
                            logger.warning(f"[Order {response.order_id}] - Not enough stock to execute order") ## Shows still successful in frontend ??? 

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
