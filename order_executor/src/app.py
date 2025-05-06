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

    def decrement_stock(self, book):
        with grpc.insecure_channel('books_database:50056') as channel:
            response: WriteResponse = BooksDatabaseStub(channel).DecrementStock(WriteRequest(
                title=book.name,
                quantity=book.quantity
            ))

            return book.name, response.success
        
    def increment_stock(self, book):
        with grpc.insecure_channel('books_database:50056') as channel:
            response: WriteResponse = BooksDatabaseStub(channel).IncrementStock(WriteRequest(
                title=book.name,
                quantity=book.quantity
            ))

            return book.name, response.success

    def execute_order(self, order: DequeueResponse):
        # Use ThreadPoolExecutor to handle multiple stock decrements concurrently
        logger.info(f"[Order {order.order_id}] - Decrementing stock for order items...")
        with futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(
                self.decrement_stock,
                order.items
            ))

        # Check if all stock decrements were successful
        if all(result[1] for result in results):
            return True

        # If any stock decrement failed, increment the stock back
        logger.error(f"[Order {order.order_id}] - Not enough stock to execute order. Rolling back...")
        with futures.ThreadPoolExecutor() as executor:
            results = executor.map(
                self.increment_stock,
                [book for book in order.items if (book.name, True) in results]
            )

        # Check if all stock increments were successful
        if not all(result[1] for result in results):
            logger.error(f"[Order {order.order_id}] - Something went wrong rolling back")

        return False

    def two_phase_commit(self, order: DequeueResponse):
        logger.info(f"[Order {order.order_id}] - Starting 2PC")

        book_prepared = False
        payment_prepared = False

        try:
            with grpc.insecure_channel("books_database:50056") as books_channel, \
                grpc.insecure_channel("payment:50057") as payment_channel:

                books_stub = BooksDatabaseStub(books_channel)
                payment_stub = PaymentServiceStub(payment_channel)

                # Send Prepare to Books
                book_prepare_resp = books_stub.Prepare(TransactionRequest(
                    order_id=order.order_id,
                    updates=[WriteRequest(title=item.name, quantity=item.quantity) for item in order.items]
                ))

                # Send Prepare to Payment
                payment_prepare_resp = payment_stub.Prepare(PaymentRequest(
                    order_id=order.order_id,
                    amount=sum(item.quantity for item in order.items) * 5 # just a dummy amount, each book costs 5
                ))

                book_prepared = book_prepare_resp.ready
                payment_prepared = payment_prepare_resp.ready

            # If both prepared, commit
            if book_prepared and payment_prepared:
                logger.info(f"[Order {order.order_id}] - Both services ready. COMMITTING...")

                with grpc.insecure_channel("books_database:50056") as books_channel, \
                    grpc.insecure_channel("payment:50057") as payment_channel:

                    BooksDatabaseStub(books_channel).Commit(TransactionRequest(order_id=order.order_id, updates=[WriteRequest(title=item.name, quantity=item.quantity) for item in order.items]))
                    PaymentServiceStub(payment_channel).Commit(PaymentRequest(order_id=order.order_id))

                return True

            raise Exception("One or more participants not ready")

        except Exception as e:
            logger.warning(f"[Order {order.order_id}] - ABORTING: {e}")

            if book_prepared:
                with grpc.insecure_channel("books_database:50056") as books_channel:
                    BooksDatabaseStub(books_channel).Abort(TransactionRequest(order_id=order.order_id, 
                                                                              updates=[WriteRequest(title=item.name, quantity=item.quantity) for item in order.items]))

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
