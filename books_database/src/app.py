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
            "Book B": Book(title="Book B", stock=1),
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
    
    def Read(self, request: ReadRequest, _):
        logger.info(f"[{request.title}] - Read request received")
        return ReadResponse(stock=self.read(request.title))

    def send_write_request(self, request: WriteRequest, peer_ip, retry = 0):
        try:
            with grpc.insecure_channel(f"{peer_ip}:50056") as channel:
                return BooksDatabaseStub(channel).Write(request).success
        except Exception:
            if retry < 3:
                return self.send_write_request(request, peer_ip, retry + 1)

            logger.warning(f"[{request.title}] - Failed to send write request to {peer_ip}:50056")
            return False
    ''' 
    def Write(self, request: WriteRequest, context):
        peer = context.peer().lstrip("ipv4:").split(":")[0]

        # Wait for the leader election to finish
        self.monitor_event.wait()
        
        # Check if the current instance is the leader
        if self.leader[0] == self.id_ip[0]:
            logger.info(f"[{request.title}] - Received write request - propagating to followers")

            # Write to the local store
            with self.store.get(request.title, Book(request.title, 0)).lock:
                self.write(request.title, request.quantity)

                # Propagate the write to followers
                with futures.ThreadPoolExecutor() as executor:
                    responses = executor.map(
                        lambda x: self.send_write_request(request, x),
                        self.peers.values()
                    )

                # Check if all followers acknowledged the write
                if all(responses):
                    logger.info(f"[{request.title}] - All followers acknowledged the write")
                    return WriteResponse(success=True)
                else:
                    logger.warning(f"[{request.title}] - Not all followers acknowledged the write")
                    return WriteResponse(success=False)
        
        # If the current instance is a follower and the message came from the leader
        elif self.leader[0] != self.id_ip[0] and peer == self.leader[1]:
            logger.debug(f"[{request.title}] - Received write request - writing to local store")

            # Write to the local store
            with self.store.get(request.title, Book(request.title, 0)).lock:
                self.write(request.title, request.quantity)
                return WriteResponse(success=True)
        
        # If the current instance is a follower and the message came from a non-leader
        elif self.leader[0] != self.id_ip[0] and peer != self.leader[1]:
            # Forward the write request to the leader
            logger.info(f"[{request.title}] - Received write request - forwarding to leader")

            try:
                with grpc.insecure_channel(f"{self.leader[1]}:50056") as channel:
                    return BooksDatabaseStub(channel).Write(request)
            except Exception:
                logger.warning(f"[{request.title}] - Failed to send write request to {self.leader[1]}:50056")
                return WriteResponse(success=False)
            
        else:
            logger.error(f"Something went wrong with the write request")
            return WriteResponse(success=False)
    '''
    '''
    def IncrementStock(self, request: WriteRequest, context):
        # Increment the stock of the book
        current_stock = self.read(request.title)

        return self.Write(WriteRequest(
            title=request.title,
            quantity=current_stock + request.quantity
        ), context)
    '''  
    '''
    def DecrementStock(self, request: WriteRequest, context):
        # Decrement the stock of the book
        current_stock = self.read(request.title)
        
        if current_stock - request.quantity < 0:
            logger.warning(f"[{request.title}] - Not enough stock to decrement. Current stock: {current_stock} , Requested : {request.quantity}")
            return WriteResponse(success=False)
        
        return self.Write(WriteRequest(
            title=request.title,
            quantity=current_stock - request.quantity
        ), context)
    '''


    def prepare_write(self,order_id, title, new_stock):
        if order_id not in self.temp_updates:
            self.temp_updates[order_id] = []

        self.temp_updates[order_id].append({'book': title, 'quantity': new_stock})

    def Prepare_write(self,request:WriteRequest,context):
        peer = context.peer().lstrip("ipv4:").split(":")[0]

        # Wait for the leader election to finish
        self.monitor_event.wait()
        
        # Check if the current instance is the leader
        if self.leader[0] == self.id_ip[0]:
            logger.info(f"[{request.title}] - Received write request - propagating to followers")

            # Write to the local store
            self.prepare_write(order_id=request.order_id, title=request.title, new_stock=request.quantity)

            # Propagate the write to followers
            with futures.ThreadPoolExecutor() as executor:
                    responses = executor.map(
                        lambda x: self.send_prepare_write(request, x),
                        self.peers.values()
                    )

            # Check if all followers acknowledged the write
            if all(responses):
                logger.info(f"[{request.title}] - All followers acknowledged the write")
                return WriteResponse(success=True)
            else:
                logger.warning(f"[{request.title}] - Not all followers acknowledged the write")
                return WriteResponse(success=False)
        
        # If the current instance is a follower and the message came from the leader
        elif self.leader[0] != self.id_ip[0] and peer == self.leader[1]:
            logger.debug(f"[{request.title}] - Received write request - writing to local store")

            # Write to the local store
            self.prepare_write(order_id=request.order_id, title=request.title, new_stock=request.quantity)
            return WriteResponse(success=True)
        
        # If the current instance is a follower and the message came from a non-leader
        elif self.leader[0] != self.id_ip[0] and peer != self.leader[1]:
            # Forward the write request to the leader
            logger.info(f"[{request.title}] - Received write request - forwarding to leader")

            try:
                with grpc.insecure_channel(f"{self.leader[1]}:50056") as channel:
                    return BooksDatabaseStub(channel).Write(request)
            except Exception:
                logger.warning(f"[{request.title}] - Failed to send write request to {self.leader[1]}:50056")
                return WriteResponse(success=False)
        else:
            logger.error(f"Something went wrong with the write request")
            return WriteResponse(success=False)

    def PrepareIncrementStock(self,request:WriteRequest,context):
        current_stock = self.read(request.title)

        return self.Prepare_write(WriteRequest(
            title=request.title, order_id = request.order_id,
            quantity=current_stock + request.quantity
        ), context)

    def PrepareDecrementStock(self,request:WriteRequest,context):
        current_stock = self.read(request.title)
        
        if current_stock - request.quantity < 0:
            logger.warning(f"[{request.title}] - Not enough stock to decrement. Current stock: {current_stock} , Requested : {request.quantity}")
            return WriteResponse(success=False)
        
        return self.Prepare_write(WriteRequest(
            title=request.title,order_id = request.order_id,
            quantity=current_stock - request.quantity
        ), context)


    def Prepare(self, request, context):
        logger.info(f"Preparing transaction for {len(request.updates)} updates")
        order_id = request.order_id if hasattr(request, 'order_id') else "global_transaction"
        
        for update in request.updates:
            logger.info(f"[{update.title}] - Preparing write of {update.quantity}")
            self.prepare_write(order_id, update.title, update.quantity)
            
        return PrepareResponse(ready=True)
    
    def Commit(self, request, context):
        logger.info(f"Committing transaction")
        order_id = request.order_id if hasattr(request, 'order_id') else "global_transaction"
        
        if order_id in self.temp_updates:
            updates = self.temp_updates[order_id]
            logger.info(f"Committing {len(updates)} updates for order {order_id}")
            
            for update in updates:
                title = update['book']
                quantity = update['quantity']
                logger.info(f"[{title}] - Committing write of {quantity}")
                self.write(title, quantity)
                
            # Clean up after commit
            del self.temp_updates[order_id]
            return CommitResponse(success=True)
        else:
            logger.warning(f"No prepared updates found for order {order_id}")
            return CommitResponse(success=False)
    
    def Abort(self, request, context):
        logger.info(f"Aborting transaction")
        order_id = request.order_id if hasattr(request, 'order_id') else "global_transaction"
        
        if order_id in self.temp_updates:
            updates = self.temp_updates[order_id]
            logger.info(f"Aborting {len(updates)} updates for order {order_id}")
            
            for update in self.temp_updates[order_id]:
                title = update['book']
                logger.info(f"[{title}] - Aborting write")
                
            # Clean up aborted transaction
            del self.temp_updates[order_id]
            
        return AbortResponse(aborted=True)
        
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
