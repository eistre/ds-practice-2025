import sys
import os

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
fraud_detection_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/fraud_detection'))
sys.path.insert(0, fraud_detection_grpc_path)
import fraud_detection_pb2 as fraud_detection
import fraud_detection_pb2_grpc as fraud_detection_grpc

transaction_verification_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/transaction_verification'))
sys.path.insert(0, transaction_verification_grpc_path)
import transaction_verification_pb2 as transaction_verification
import transaction_verification_pb2_grpc as transaction_verification_grpc

import grpc

def detect_fraud(request, order_id):
    # Establish a connection with the fraud-detection gRPC service.
    with grpc.insecure_channel('fraud_detection:50051') as channel:
        # Create a stub object.
        stub = fraud_detection_grpc.FraudDetectionServiceStub(channel)
        # Call the service through the stub object.
        response = stub.DetectFraud(fraud_detection.FraudDetectionRequest(
            orderId=order_id,
            user=fraud_detection.User(
                name=request["user"]["name"],
                contact=request["user"]["contact"]
            ),
            items=[
                fraud_detection.Item(name=item["name"], quantity=item["quantity"]) for item in request["items"]
            ],
            billingAddress=fraud_detection.Address(
                street=request["billingAddress"]["street"],
                city=request["billingAddress"]["city"],
                state=request["billingAddress"]["state"],
                zip=request["billingAddress"]["zip"],
                country=request["billingAddress"]["country"]
            ),
            shippingMethod=request["shippingMethod"]
        ))

    return response

def verify_transaction(request, order_id):
    # Establish a connection with the transaction_verification gRPC service.
    with grpc.insecure_channel('transaction_verification:50052') as channel:
        # Create a stub object.
        stub = transaction_verification_grpc.TransactionVerificationServiceStub(channel)
        # Call the service through the stub object.
        response = stub.VerifyTransaction(transaction_verification.TransactionVerificationRequest(
            orderId=order_id,
            user=transaction_verification.User(
                name=request["user"]["name"],
                contact=request["user"]["contact"]
            ),
            items=[
                transaction_verification.Item(name=item["name"], quantity=item["quantity"]) for item in request["items"]
            ],
            creditCard=transaction_verification.CreditCard(
                number=request["creditCard"]["number"],
                expirationDate=request["creditCard"]["expirationDate"],
                cvv=request["creditCard"]["cvv"]
            )
        ))

    return response

# Import Flask.
# Flask is a web framework for Python.
# It allows you to build a web application quickly.
# For more information, see https://flask.palletsprojects.com/en/latest/
from flask import Flask, request
from flask_cors import CORS
import json

# Create a simple Flask app.
app = Flask(__name__)
# Enable CORS for the app.
CORS(app, resources={r'/*': {'origins': '*'}})

@app.route('/checkout', methods=['POST'])
def checkout():
    """
    Responds with a JSON object containing the order ID, status, and suggested books.
    """

    try:
        # Get request object data to json
        request_data = json.loads(request.data)
        order_id = 12345

        print(f"Received checkout request, given order ID: {order_id}")

        # Validate request object data
        if any(key not in request_data for key in ["user", "creditCard", "items", "billingAddress", "shippingMethod", "giftWrapping", "termsAccepted"]) or \
            any(key not in request_data["user"] for key in ["name", "contact"]) or \
            any(key not in request_data["creditCard"] for key in ["number", "expirationDate", "cvv"]) or \
            any(key not in request_data["billingAddress"] for key in ["street", "city", "state", "zip", "country"]):
            
            print(f"Invalid request for order {order_id}")
            return {
                "error": {
                    "code": 400,
                    "message": "Invalid request"
                }
            }, 400

        # Call the fraud detection and transaction verification services
        fraud_detection_response = detect_fraud(request_data, order_id)
        transaction_verification_response = verify_transaction(request_data, order_id)

        if fraud_detection_response.isFraudulent or not transaction_verification_response.isVerified:
            print(f"Order {order_id} is fraudulent or not verified")
            return {
                "orderId": order_id,
                "status": "Order Rejected",
                "suggestedBooks": []
            }, 200

        # Dummy response following the provided YAML specification for the bookstore
        order_status_response = {
            'orderId': order_id,
            'status': 'Order Approved',
            'suggestedBooks': [
                {'bookId': '123', 'title': 'The Best Book', 'author': 'Author 1'},
                {'bookId': '456', 'title': 'The Second Best Book', 'author': 'Author 2'}
            ]
        }

        return order_status_response
    
    except Exception as e:
        print(f"Error during checkout: {e}")
        return {
            "error": {
                "code": 500,
                "message": "An error occurred"
            }
        }, 500


if __name__ == '__main__':
    # Run the app in debug mode to enable hot reloading.
    # This is useful for development.
    # The default port is 5000.
    app.run(host='0.0.0.0')
