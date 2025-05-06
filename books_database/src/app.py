import sys
import os

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
books_database_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb'))
sys.path.insert(0, books_database_grpc_path)
from books_database.books_database_pb2 import *
from books_database.books_database_pb2_grpc import *
from leader_election_service import LeaderElectionService
from utils.utils_pb2_grpc import add_LeaderElectionServiceServicer_to_server

import grpc
import logging
import threading
from concurrent import futures

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] - [%(levelname)s] - [Books Database] - [Thread %(thread)d] - %(message)s"
)

logger = logging.getLogger()

class Book:
    def __init__(self, title, stock):
        self.title = title
        self.stock = stock
        self.lock = threading.RLock()

# Class for books database
class BooksDatabase(BooksDatabaseServicer, LeaderElectionService):
    def __init__(self):
        # Initialize store with some sample data
        self.store: dict[str, Book] = {
            "Book A": Book(title="Book A", stock=10),
            "Book B": Book(title="Book B", stock=5),
        }
        self.temp_updates = {}

        super().__init__(service_name="books_database", port="50056", logger=logger)
        logger.info(f"Books Database is initialized with ID: {self.id_ip[0]}")

    def read(self, title):
        if title not in self.store:
            return 0
        
        with self.store[title].lock:
            return self.store[title].stock
      
    def write(self, title, new_stock):
        with (book := self.store.get(title, Book(title, 0))).lock:
            book.stock = new_stock
            self.store[title] = book
    
    def prepare_write(self,order_id, title, new_stock):
        if order_id not in self.temp_updates:
            self.temp_updates[order_id] = {}

        self.temp_updates[order_id][title] = new_stock

    def Read(self, request: ReadRequest, _):
        logger.info(f"[{request.title}] - Read request received")
        return ReadResponse(stock=self.read(request.title))

    def send_commit_write(self, request: TransactionRequest, peer_ip, retry = 0):
        try:
            with grpc.insecure_channel(f"{peer_ip}:50056") as channel:
                return BooksDatabaseStub(channel).CommitWrite(request).success
        except Exception:
            if retry < 3:
                return self.send_commit_write(request, peer_ip, retry + 1)

            logger.warning(f"[{request.title}] - Failed to send commit write to {peer_ip}:50056")
            return False
    
    def send_abort_write(self, request: TransactionRequest, peer_ip, retry = 0):
        try:
            with grpc.insecure_channel(f"{peer_ip}:50056") as channel:
                return BooksDatabaseStub(channel).AbortWrite(request).aborted
        except Exception:
            if retry < 3:
                return self.send_abort_write(request, peer_ip, retry + 1)

            logger.warning(f"[{request.title}] - Failed to send write abort to {peer_ip}:50056")
            return False

    def send_prepare_write(self, request: WriteRequest, peer_ip, retry=0):
        try:
            with grpc.insecure_channel(f"{peer_ip}:50056") as channel:
                return BooksDatabaseStub(channel).PrepareWrite(request).ready
        except Exception:
            if retry < 3:
                return self.send_prepare_write(request, peer_ip, retry + 1)
            
            logger.warning(f"[{request.title}] - Failed to send prepare write to {peer_ip}:50056")
            return False
     
    def CommitWrite(self, request: TransactionRequest, context):
        peer = context.peer().lstrip("ipv4:").split(":")[0]

        # Wait for the leader election to finish
        self.monitor_event.wait()
        
        # Check if the current instance is the leader
        if self.leader[0] == self.id_ip[0]:
            logger.info(f"[Order {request.order_id}] - Received write commit - propagating to followers")

            # Write to the local store
            for title in list(self.temp_updates[request.order_id]):
                with self.store.get(title, Book(title, 0)).lock:
                    self.write(title, self.temp_updates[request.order_id].pop(title))

            # Delete from the temp store
            del self.temp_updates[request.order_id]

            # Propagate the write to followers
            with futures.ThreadPoolExecutor() as executor:
                responses = executor.map(
                    lambda x: self.send_commit_write(request, x),
                    self.peers.values()
                )

            # Check if all followers acknowledged the write
            if all(responses):
                logger.info(f"[Order {request.order_id}] - All followers acknowledged the write commit")
                return CommitResponse(success=True)
            else:
                logger.warning(f"[Order {request.order_id}] - Not all followers acknowledged the write commit")
                return CommitResponse(success=False)
        
        # If the current instance is a follower and the message came from the leader
        elif self.leader[0] != self.id_ip[0] and peer == self.leader[1]:
            logger.debug(f"[Order {request.order_id}] - Received write commit - writing to local store")

            # Write to the local store
            for title in list(self.temp_updates[request.order_id]):
                with self.store.get(title, Book(title, 0)).lock:
                    self.write(title, self.temp_updates[request.order_id].pop(title))

            # Delete from the temp store
            del self.temp_updates[request.order_id]
 
            return CommitResponse(success=True)
        
        # If the current instance is a follower and the message came from a non-leader
        elif self.leader[0] != self.id_ip[0] and peer != self.leader[1]:
            # Forward the write request to the leader
            logger.info(f"[Order {request.order_id}] - Received write commit - forwarding to leader")

            try:
                with grpc.insecure_channel(f"{self.leader[1]}:50056") as channel:
                    return BooksDatabaseStub(channel).CommitWrite(request)
            except Exception:
                logger.warning(f"[Order {request.order_id}] - Failed to send write commit to {self.leader[1]}:50056")
                return CommitResponse(success=False)
            
        else:
            logger.error(f"Something went wrong with the write commit")
            return CommitResponse(success=False)
    
    def AbortWrite(self, request: TransactionRequest, context):
        peer = context.peer().lstrip("ipv4:").split(":")[0]

        # Wait for the leader election to finish
        self.monitor_event.wait()
        
        # Check if the current instance is the leader
        if self.leader[0] == self.id_ip[0]:
            logger.info(f"[Order {request.order_id}] - Received write abort - propagating to followers")

            # Delete from the temp store
            del self.temp_updates[request.order_id]

            # Propagate the write to followers
            with futures.ThreadPoolExecutor() as executor:
                responses = executor.map(
                    lambda x: self.send_abort_write(request, x),
                    self.peers.values()
                )

            # Check if all followers acknowledged the write
            if all(responses):
                logger.info(f"[Order {request.order_id}] - All followers acknowledged the write abort")
                return AbortResponse(aborted=True)
            else:
                logger.warning(f"[Order {request.order_id}] - Not all followers acknowledged the write abort")
                return AbortResponse(aborted=False)
        
        # If the current instance is a follower and the message came from the leader
        elif self.leader[0] != self.id_ip[0] and peer == self.leader[1]:
            logger.debug(f"[Order {request.order_id}] - Received write abort - deleting from local temp store")

            # Write to the local store
            del self.temp_updates[request.order_id]
            return AbortResponse(aborted=True)
        
        # If the current instance is a follower and the message came from a non-leader
        elif self.leader[0] != self.id_ip[0] and peer != self.leader[1]:
            # Forward the write request to the leader
            logger.info(f"[{request.title}] - Received write abort - forwarding to leader")

            try:
                with grpc.insecure_channel(f"{self.leader[1]}:50056") as channel:
                    return BooksDatabaseStub(channel).AbortWrite(request)
            except Exception:
                logger.warning(f"[Order {request.order_id}] - Failed to send write abort to {self.leader[1]}:50056")
                return AbortResponse(aborted=False)
            
        else:
            logger.error(f"Something went wrong with the write abort")
            return AbortResponse(aborted=False)

    def PrepareWrite(self, request: WriteRequest, context):
        peer = context.peer().lstrip("ipv4:").split(":")[0]

        # Wait for the leader election to finish
        self.monitor_event.wait()
        
        # Check if the current instance is the leader
        if self.leader[0] == self.id_ip[0]:
            logger.info(f"[{request.title}] - Received write prepare - propagating to followers")

            # Write to the temp store
            self.prepare_write(request.order_id, request.title, request.quantity)

            # Propagate the write to followers
            with futures.ThreadPoolExecutor() as executor:
                responses = executor.map(
                    lambda x: self.send_prepare_write(request, x),
                    self.peers.values()
                )

            # Check if all followers acknowledged the write
            if all(responses):
                logger.info(f"[{request.title}] - All followers acknowledged the write prepare")
                return PrepareResponse(ready=True)
            else:
                logger.warning(f"[{request.title}] - Not all followers acknowledged the write prepare")
                return PrepareResponse(ready=False)
        
        # If the current instance is a follower and the message came from the leader
        elif self.leader[0] != self.id_ip[0] and peer == self.leader[1]:
            logger.debug(f"[{request.title}] - Received write prepare - writing to local store")

            # Write to the temp store
            self.prepare_write(request.order_id, request.title, request.quantity)
            return PrepareResponse(ready=True)
        
        # If the current instance is a follower and the message came from a non-leader
        elif self.leader[0] != self.id_ip[0] and peer != self.leader[1]:
            # Forward the write request to the leader
            logger.info(f"[{request.title}] - Received write prepare - forwarding to leader")

            try:
                with grpc.insecure_channel(f"{self.leader[1]}:50056") as channel:
                    return BooksDatabaseStub(channel).PrepareWrite(request)
            except Exception:
                logger.warning(f"[{request.title}] - Failed to send write prepare to {self.leader[1]}:50056")
                return PrepareResponse(ready=False)
            
        else:
            logger.error(f"Something went wrong with the write prepare")
            return PrepareResponse(ready=False)

    def PrepareIncrementStock(self, request: WriteRequest, context):
        current_stock = self.read(request.title)

        return self.PrepareWrite(WriteRequest(
            title=request.title,
            order_id = request.order_id,
            quantity=current_stock + request.quantity
        ), context)
    
    def PrepareDecrementStock(self, request: WriteRequest, context):
        current_stock = self.read(request.title)
        
        if current_stock - request.quantity < 0:
            logger.warning(f"[{request.title}] - Not enough stock to decrement. Current stock: {current_stock} , Requested : {request.quantity}")
            return PrepareResponse(ready=False)
        
        return self.PrepareWrite(WriteRequest(
            title=request.title,
            order_id=request.order_id,
            quantity=current_stock - request.quantity
        ), context)
        
def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add the books database service to the server
    books_database = BooksDatabase()
    add_BooksDatabaseServicer_to_server(books_database, server)
    add_LeaderElectionServiceServicer_to_server(books_database, server)
    # Listen on port 50056
    port = "50056"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    logger.info("Server started. Listening on port 50056.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
