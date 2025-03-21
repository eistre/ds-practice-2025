import sys
import os

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
sys.path.insert(0, os.path.abspath(os.path.join(FILE, f"../../../../utils/pb/transaction_verification")))

import grpc
import logging
from concurrent import futures
import transaction_verification_pb2 as transaction_verification
import transaction_verification_pb2_grpc as transaction_verification_grpc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] - [%(levelname)s] - [Orchestrator] - [Thread %(thread)d] - %(message)s"
)

logger = logging.getLogger()

def initialize_transaction_verification(request, order_id):
    with grpc.insecure_channel('transaction_verification:50052') as channel:
        stub = transaction_verification_grpc.TransactionVerificationServiceStub(channel)
        stub.InitOrder(transaction_verification.InitializationRequest(
            order_id=order_id,
            user=transaction_verification.User(
                name=request["user"]["name"],
                contact=request["user"]["contact"],
                address=transaction_verification.Address(
                    street=request["billingAddress"]["street"],
                    city=request["billingAddress"]["city"],
                    state=request["billingAddress"]["state"],
                    zip=request["billingAddress"]["zip"],
                    country=request["billingAddress"]["country"]
                )
            ),
            items=[
                transaction_verification.Item(name=item["name"], quantity=item["quantity"]) for item in request["items"]
            ],
            credit_card=transaction_verification.CreditCard(
                number=request["creditCard"]["number"],
                expiration_date=request["creditCard"]["expirationDate"],
                cvv=request["creditCard"]["cvv"]
            )
        ))

def verify_order_items(order_id):
    with grpc.insecure_channel('transaction_verification:50052') as channel:
        stub = transaction_verification_grpc.TransactionVerificationServiceStub(channel)
        response: transaction_verification.VerificationResponse = stub.VerifyItems(transaction_verification.ContinuationRequest(order_id=order_id))

        if not response.verified:
            raise Exception(f"[Order {order_id}] - Order items: verification failed")
        
        logger.info(f"[Order {order_id}] - Order items: verified")
        
def verify_user_data(order_id):
    with grpc.insecure_channel('transaction_verification:50052') as channel:
        stub = transaction_verification_grpc.TransactionVerificationServiceStub(channel)
        response: transaction_verification.VerificationResponse = stub.VerifyUserData(transaction_verification.ContinuationRequest(order_id=order_id))

        if not response.verified:
            raise Exception(f"[Order {order_id}] - User data: verification failed")

        logger.info(f"[Order {order_id}] - User data: verified")

def verify_credit_card(order_id, verify_order_items_future: futures.Future[None]):
    # Wait for the order items to be verified
    verify_order_items_future.result()

    with grpc.insecure_channel('transaction_verification:50052') as channel:
        stub = transaction_verification_grpc.TransactionVerificationServiceStub(channel)
        response: transaction_verification.VerificationResponse = stub.VerifyCreditCard(transaction_verification.ContinuationRequest(order_id=order_id))
        
        if not response.verified:
            raise Exception(f"[Order {order_id}] - Credit card: verification failed")
        
        logger.info(f"[Order {order_id}] - Credit card: verified")
