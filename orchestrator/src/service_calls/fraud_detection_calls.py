import sys
import os

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
sys.path.insert(0, os.path.abspath(os.path.join(FILE, f"../../../../utils/pb")))

import grpc
import logging
from concurrent import futures
import utils.utils_pb2 as utils
import fraud_detection.fraud_detection_pb2 as fraud_detection
import fraud_detection.fraud_detection_pb2_grpc as fraud_detection_grpc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] - [%(levelname)s] - [Orchestrator] - [Thread %(thread)d] - %(message)s"
)

logger = logging.getLogger()

def initialize_fraud_detection(request, order_id):
    with grpc.insecure_channel('fraud_detection:50051') as channel:
        stub = fraud_detection_grpc.FraudDetectionServiceStub(channel)
        stub.InitOrder(fraud_detection.InitializationRequest(
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
            credit_card=utils.CreditCard(
                number=request["creditCard"]["number"],
                expiration_date=request["creditCard"]["expirationDate"],
                cvv=request["creditCard"]["cvv"]
            )
        ))

def check_user_data(order_id, verify_user_data_future: futures.Future[list[int]]):
    # Wait for user data to be verified
    vector_clock = verify_user_data_future.result()
    
    with grpc.insecure_channel('fraud_detection:50051') as channel:
        stub = fraud_detection_grpc.FraudDetectionServiceStub(channel)
        response: fraud_detection.DetectionResponse = stub.CheckUserData(utils.ContinuationRequest(
            order_id=order_id,
            vector_clocks=[utils.VectorClock(clock=vector_clock)]
        ))

        if response.is_fraud:
            raise Exception(order_id,response.vector_clock.clock, "User data: fraud detected")
        
        logger.info(f"[Order {order_id}] - User data: not fraudulent")
        return response.vector_clock.clock

def check_credit_card(order_id, vector_clocks):
    with grpc.insecure_channel('fraud_detection:50051') as channel:
        stub = fraud_detection_grpc.FraudDetectionServiceStub(channel)
        response: fraud_detection.DetectionResponse = stub.CheckCreditCard(utils.ContinuationRequest(
            order_id=order_id,
            vector_clocks=[utils.VectorClock(clock=vector_clock) for vector_clock in vector_clocks]
        ))

        if response.is_fraud:
            raise Exception(order_id,response.vector_clock.clock, "Credit card: fraud detected")
        
        logger.info(f"[Order {order_id}] - Credit card: not fraudulent")
        return response.vector_clock.clock

def clear_fraud_detection(order_id,vector_clock):
    with grpc.insecure_channel('fraud_detection:50051') as channel:
        stub = fraud_detection_grpc.FraudDetectionServiceStub(channel)
        stub.ClearOrder(utils.ClearRequest(order_id=order_id,vector_clock=utils.VectorClock(clock=vector_clock)))
