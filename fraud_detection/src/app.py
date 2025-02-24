import sys
import os

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
fraud_detection_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/fraud_detection'))
sys.path.insert(0, fraud_detection_grpc_path)
from fraud_detection_pb2 import *
from fraud_detection_pb2_grpc import *

import grpc
import json
from concurrent import futures
from google import genai
from pydantic import BaseModel

class AIResponse(BaseModel):
    isFraudulent: bool
    reasons: list[str]

AI_FRAUD_DETECTION_PROMPT = """
    You are an expert fraud detection analyst with years of experience in e-commerce security.
    Analyze the following order for potential fraud by applying industry best practices and pattern recognition.
    Even if you determine the order is used as test data, provide a thorough analysis to demonstrate your expertise.

    Consider these key factors:
    1. User details (name and contact) - check for suspicious patterns
    2. Order items (name and quantity) - analyze for unusual purchasing behavior
    3. Billing address details - verify location consistency
    4. Shipping method - evaluate for high-risk shipping patterns

    Based on your expert analysis, determine if this order appears fraudulent. Return:
    - A boolean indicating if the order is fraudulent

    Respond only in valid JSON format with this structure:
    {
        "isFraudulent": boolean,
    }

    Here is the order to analyze:

"""

# Class for fraud detection
class FraudDetectionService(FraudDetectionServiceServicer):

    def __init__(self):
        # Initialize google genai client
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        print("Google genai client initialized")

    def DetectFraud(self, request: FraudDetectionRequest, _):
        # Create a FraudDetection response
        response = FraudDetectionResponse()
        response.isFraudulent = False
        print(f"Received request for fraud detection for order {request.orderId}")

        # Perform simple fraud detection
        if len(request.items) > 10:
            print(f"Too many items in order {request.orderId}")
            response.isFraudulent = True
            return response
        
        if any(item.quantity > 20 for item in request.items):
            print(f"Too many of a single item in order {request.orderId}")
            response.isFraudulent = True
            return response

        # Complex fraud detection via AI
        ai_response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=AI_FRAUD_DETECTION_PROMPT + json.dumps({
                "user": {
                    "name": request.user.name,
                    "contact": request.user.contact
                },
                "items": [
                    {"name": item.name, "quantity": item.quantity} for item in request.items
                ],
                "billingAddress": {
                    "street": request.billingAddress.street,
                    "city": request.billingAddress.city,
                    "state": request.billingAddress.state,
                    "zip": request.billingAddress.zip,
                    "country": request.billingAddress.country
                },
                "shippingMethod": request.shippingMethod
            }),
            config={
                "response_mime_type": "application/json",
                "response_schema": AIResponse,
                "candidate_count": 1
            }
        )

        # Parse AI response
        ai_response: AIResponse = ai_response.parsed

        # Update response
        response.isFraudulent = ai_response.isFraudulent or response.isFraudulent
        print(f"Fraud detection for order {request.orderId}:", ai_response.isFraudulent)

        return response

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
    print("Server started. Listening on port 50051.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
