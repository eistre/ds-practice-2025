import sys
import os

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
fraud_detection_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb'))
sys.path.insert(0, fraud_detection_grpc_path)
from utils.utils_pb2 import *
from fraud_detection.fraud_detection_pb2 import *
from fraud_detection.fraud_detection_pb2_grpc import *

import grpc
import json
import logging
import datetime
from google import genai
from concurrent import futures
from pydantic import BaseModel
from google.protobuf import empty_pb2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] - [%(levelname)s] - [Fraud Detection] - [Thread %(thread)d] - %(message)s"
)

logger = logging.getLogger()

class AIResponse(BaseModel):
    is_fraud: bool

AI_USER_DATA = """
    You are an expert fraud detection analyst with years of experience in e-commerce security.
    Analyze the following user data for potential fraud by applying industry best practices and pattern recognition.
    Even if you determine the order is used as test data, provide a thorough analysis to demonstrate your expertise.

    Consider these key factors:
    1. User details (name and contact) - check for suspicious patterns
    2. Address details - verify location consistency

    Based on your expert analysis, determine if this order appears fraudulent. Return:
    - A boolean indicating if the order is fraudulent

    Respond only in valid JSON format with this structure:
    {
        "is_fraud": boolean,
    }

    Here is the order to analyze:

"""

AI_CREDIT_CARD = """
    You are an expert fraud detection analyst with years of experience in e-commerce security.
    Analyze the following credit card data for potential fraud by applying industry best practices and pattern recognition.
    Even if you determine the order is used as test data, provide a thorough analysis to demonstrate your expertise.

    Consider these key factors:
    1. Credit card number - check for suspicious patterns
    2. Expiration date - verify if the card is expired
    3. CVV - verify if the CVV is valid

    Based on your expert analysis, determine if this order appears fraudulent. Return:
    - A boolean indicating if the order is fraudulent

    Respond only in valid JSON format with this structure:
    {
        "is_fraud": boolean,
    }

    Here is the order to analyze:

"""

# Class for fraud detection
class FraudDetectionService(FraudDetectionServiceServicer):
    def __init__(self):
        # Initialize google genai client
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.orders: dict[str, InitializationRequest] = {}
        logger.info("Fraud detection service initialized")

    def InitOrder(self, request: InitializationRequest, _):
        self.orders[request.order_id] = request
        logger.info(f"[Order {request.order_id}] - Order initialized")
        return empty_pb2.Empty()
    
    def ClearOrder(self, request: ContinuationRequest, _):
        if request.order_id in self.orders:
            del self.orders[request.order_id]
            logger.info(f"[Order {request.order_id}] - Order cleared")
        return empty_pb2.Empty()

    def CheckUserData(self, request: ContinuationRequest, _):
        logger.info(f"[Order {request.order_id}] - Received request for user data fraud detection")

        # Check if the order exists
        if request.order_id not in self.orders:
            logger.info(f"[Order {request.order_id}] - Order not found - user data fraud detection failed")
            return DetectionResponse(is_fraud=False)
        
        user = self.orders[request.order_id].user

        # Use AI fraud detection for user data
        ai_response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=AI_USER_DATA + json.dumps({
                "user": {
                    "name": user.name,
                    "contact": user.contact
                },
                "address":{
                    "street": user.address.street,
                    "city": user.address.city,
                    "state": user.address.state,
                    "zip": user.address.zip,
                    "country": user.address.country
                }
            }),
            config={
                "response_mime_type": "application/json",
                "response_schema": AIResponse,
                "candidate_count": 1
            }
        )

        # Parse AI response
        ai_response: AIResponse = ai_response.parsed
        logger.info(f"[Order {request.order_id}] - User data fraud detection result: {'fraud' if ai_response.is_fraud else 'not fraudulent'}")
        return DetectionResponse(is_fraud=ai_response.is_fraud)
    
    def CheckCreditCard(self, request: ContinuationRequest, _):
        logger.info(f"[Order {request.order_id}] - Received request for credit card fraud detection")

        # Check if the order exists
        if request.order_id not in self.orders:
            logger.info(f"[Order {request.order_id}] - Order not found: credit card fraud detection failed")
            return DetectionResponse(is_fraud=False)
        
        credit_card = self.orders[request.order_id].credit_card

        # Use AI fraud detection for credit card
        ai_response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=AI_CREDIT_CARD + json.dumps({
                "credit_card": {
                    "number": credit_card.number,
                    "expiration": credit_card.expiration_date,
                    "cvv": credit_card.cvv
                },
                "date": datetime.datetime.now().strftime("%Y-%m-%d")
            }),
            config={
                "response_mime_type": "application/json",
                "response_schema": AIResponse,
                "candidate_count": 1
            }
        )

        # Parse AI response
        ai_response: AIResponse = ai_response.parsed
        logger.info(f"[Order {request.order_id}] - Credit card fraud detection result: {'fraud' if ai_response.is_fraud else 'not fraudulent'}")
        return DetectionResponse(is_fraud=ai_response.is_fraud)

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add the fraud detection service to the server
    add_FraudDetectionServiceServicer_to_server(FraudDetectionService(), server)
    # Listen on port 50051
    port = "50051"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    logger.info("Server started. Listening on port 50051.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
