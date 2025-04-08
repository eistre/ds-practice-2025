import sys
import os

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
fraud_detection_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb'))
sys.path.insert(0, fraud_detection_grpc_path)
from utils.utils_pb2 import *
from vector_clock import VectorClock as VC
from transaction_verification.transaction_verification_pb2 import *
from transaction_verification.transaction_verification_pb2_grpc import *

import grpc
import datetime
import logging
from concurrent import futures
from google.protobuf import empty_pb2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] - [%(levelname)s] - [Transaction] - [Thread %(thread)d] - %(message)s"
)

logger = logging.getLogger()

# Class for transaction verification
class TransactionVerificationService(TransactionVerificationServiceServicer):
    def __init__(self, svc_idx=0, total_svcs=3):
        self.orders: dict[str, dict[str, InitializationRequest | VC]] = {}
        self.svc_idx = svc_idx
        self.total_svcs = total_svcs
        logger.info(f"Transaction verification service initialized (index: {svc_idx}, total services: {total_svcs})")

    def InitOrder(self, request: InitializationRequest, _):
        self.orders[request.order_id] = {"data": request, "vc": VC(size=self.total_svcs)}
        logger.info(f"[Order {request.order_id}] - Order initialized")
        return empty_pb2.Empty()
    
    def ClearOrder(self, request: ClearRequest, _):
        clock_check = self.orders[request.order_id]["vc"].compare(request.vector_clock.clock)
        if request.order_id in self.orders and clock_check:
            del self.orders[request.order_id]
            logger.info(f"[Order {request.order_id}] - Order cleared")
        else:
            logger.error(f"[Order {request.order_id}] - Failed to clear order.")
        return empty_pb2.Empty()

    def VerifyItems(self, request: ContinuationRequest, _):
        logger.info(f"[Order {request.order_id}] - Item verification request received")

        # Increment the vector clock
        self.orders[request.order_id]["vc"].merge_and_increment(self.svc_idx, request.vector_clocks)
        logger.info(f"Vector clock (VerifyItems): {self.orders[request.order_id]['vc'].get()}")

        # Check if the order exists
        if request.order_id not in self.orders:
            logger.info(f"[Order {request.order_id}] - Order not found: item verification failed")
            return VerificationResponse(verified=False, vector_clock=VectorClock(clock=self.orders[request.order_id]["vc"].get()))
        
        items = self.orders[request.order_id]["data"].items
        
        # Check if there are no items
        if len(items) == 0:
            logger.info(f"[Order {request.order_id}] - Order has no items: item verification failed")
            return VerificationResponse(verified=False, vector_clock=VectorClock(clock=self.orders[request.order_id]["vc"].get()))
        
        # Check if there are no zero/negative quantity items
        for item in items:
            if item.quantity <= 0:
                logger.info(f"[Order {request.order_id}] - Order has zero/negative quantity items: item verification failed")
                return VerificationResponse(verified=False, vector_clock=VectorClock(clock=self.orders[request.order_id]["vc"].get()))
        
        logger.info(f"[Order {request.order_id}] - Item verification successful")
        return VerificationResponse(verified=True, vector_clock=VectorClock(clock=self.orders[request.order_id]["vc"].get()))

    def VerifyUserData(self, request: ContinuationRequest, _):
        logger.info(f"[Order {request.order_id}] - User data verification request received")
        
        # Increment the vector clock
        self.orders[request.order_id]["vc"].merge_and_increment(self.svc_idx, request.vector_clocks)
        logger.info(f"Vector clock (VerifyUserData): {self.orders[request.order_id]['vc'].get()}")

        # Check if the order exists
        if request.order_id not in self.orders:
            logger.info(f"[Order {request.order_id}] - Order not found: user data verification failed")
            return VerificationResponse(verified=False, vector_clock=VectorClock(clock=self.orders[request.order_id]["vc"].get()))
        
        user = self.orders[request.order_id]["data"].user
        
        # Check if all user details are provided
        if not user.name or not user.contact or not user.address:
            logger.info(f"[Order {request.order_id}] - User details missing: user data verification failed")
            return VerificationResponse(verified=False, vector_clock=VectorClock(clock=self.orders[request.order_id]["vc"].get()))
        
        # Check if all address details are provided
        if not user.address.street or not user.address.city or not user.address.state or not user.address.zip or not user.address.country:
            logger.info(f"[Order {request.order_id}] - Address details missing: user data verification failed")
            return VerificationResponse(verified=False, vector_clock=VectorClock(clock=self.orders[request.order_id]["vc"].get()))
        
        logger.info(f"[Order {request.order_id}] - User data verification successful")
        return VerificationResponse(verified=True, vector_clock=VectorClock(clock=self.orders[request.order_id]["vc"].get()))

    def luhn_algorithm(self, credit_card):
        """
        Perform Luhn algorithm to validate credit card number.
        Received help from ChatGPT.
        """
        # Reverse the credit card number
        credit_card = credit_card[::-1]

        # Initialize the sum
        sum = 0

        # Loop through the credit card number
        for i in range(len(credit_card)):
            # Multiply every second digit by 2
            if i % 2 == 1:
                digit = int(credit_card[i]) * 2
                # Subtract 9 if the result is greater than 9
                if digit > 9:
                    digit -= 9
                sum += digit
            else:
                sum += int(credit_card[i])

        # Check if the sum is divisible by 10
        return sum % 10 == 0

    def VerifyCreditCard(self, request: ContinuationRequest, _):
        logger.info(f"[Order {request.order_id}] - Credit card verification request received")
        
        # Increment the vector clock
        self.orders[request.order_id]["vc"].merge_and_increment(self.svc_idx, request.vector_clocks)
        logger.info(f"Vector clock (VerifyCreditCard): {self.orders[request.order_id]['vc'].get()}")

        # Check if the order exists
        if request.order_id not in self.orders:
            logger.info(f"[Order {request.order_id}] - Order not found: credit card verification failed")
            return VerificationResponse(verified=False, vector_clock=VectorClock(clock=self.orders[request.order_id]["vc"].get()))
        
        credit_card = self.orders[request.order_id]["data"].credit_card

        # Check if the credit card expiry date is valid
        month, year = credit_card.expiration_date.split("/")
        if int(month) > 12 or int(month) < 1:
            logger.info(f"[Order {request.order_id}] - Invalid month in credit card expiration date: credit card verification failed")
            return VerificationResponse(verified=False, vector_clock=VectorClock(clock=self.orders[request.order_id]["vc"].get()))
        
        if int("20" + year) < datetime.datetime.now().year or (int("20" + year) == datetime.datetime.now().year and int(month) < datetime.datetime.now().month):
            logger.info(f"[Order {request.order_id}] - Credit card expired: credit card verification failed")
            return VerificationResponse(verified=False, vector_clock=VectorClock(clock=self.orders[request.order_id]["vc"].get()))
        
        # Check if the credit card number is valid via Luhn algorithm
        if not self.luhn_algorithm(credit_card.number):
            logger.info(f"[Order {request.order_id}] - Invalid credit card number: credit card verification failed")
            return VerificationResponse(verified=False, vector_clock=VectorClock(clock=self.orders[request.order_id]["vc"].get()))

        logger.info(f"[Order {request.order_id}] - Credit card verification successful")
        return VerificationResponse(verified=True, vector_clock=VectorClock(clock=self.orders[request.order_id]["vc"].get()))

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add the fraud detection service to the server
    add_TransactionVerificationServiceServicer_to_server(TransactionVerificationService(), server)
    # Listen on port 50052
    port = "50052"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    logger.info("Server started. Listening on port 50052.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
