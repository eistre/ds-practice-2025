import sys
import os

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
fraud_detection_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/transaction_verification'))
sys.path.insert(0, fraud_detection_grpc_path)
from transaction_verification_pb2 import *
from transaction_verification_pb2_grpc import *

import grpc
import datetime
from concurrent import futures

# Class for transaction verification
class TransactionVerificationService(TransactionVerificationServiceServicer):

    def __init__(self):
        print("Transaction verification service initialized")

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

    def VerifyTransaction(self, request: TransactionVerificationRequest, _):
        # Create a TransactionVerification response
        response = TransactionVerificationResponse()
        print(f"Received request for transaction verification for order {request.orderId}")

        # Perform simple transaction verification
        if len(request.items) == 0:
            print(f"Order {request.orderId} has no items - transaction verification failed")
            response.isVerified = False
            return response


        # Check if there are no zero quantity items
        for item in request.items:
            if item.quantity <= 0:
                print(f"Order {request.orderId} has an item with invalid quantity - transaction verification failed")
                response.isVerified = False
                return response
            
        # Check if all user details are provided
        if not request.user.name or not request.user.contact:
            print(f"Order {request.orderId} is missing user details - transaction verification failed")
            response.isVerified = False
            return response

        # Check if credit card details are valid via Luhn algorithm
        if not self.luhn_algorithm(request.creditCard.number):
            print(f"Order {request.orderId} has an invalid credit card number - transaction verification failed")
            response.isVerified = False
            return response
        
        # Check if the credit card expiry date is valid
        month, year = request.creditCard.expirationDate.split("/")
        if int(month) > 12 or int(month) < 1:
            print(f"Order {request.orderId} has an invalid credit card expiration date - transaction verification failed")
            response.isVerified = False
            return response
        
        if int("20" + year) < datetime.datetime.now().year or (int("20" + year) == datetime.datetime.now().year and int(month) < datetime.datetime.now().month):
            print(f"Order {request.orderId} has an expired credit card - transaction verification failed")
            response.isVerified = False
            return response

        # Verify transaction
        print(f"Order {request.orderId} has passed transaction verification")
        response.isVerified = True

        return response


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
    print("Server started. Listening on port 50052.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
