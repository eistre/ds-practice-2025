import uuid
import logging
from concurrent import futures
from service_calls.suggestions_calls import *
from service_calls.fraud_detection_calls import *
from service_calls.transaction_verification_calls import *

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] - [%(levelname)s] - [Orchestrator] - [Thread %(thread)d] - %(message)s"
)

logger = logging.getLogger()

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

        # Generate a unique order ID
        order_id = str(uuid.uuid4())
        logger.info(f"[Order {order_id}] - Checkout request received")

        with futures.ThreadPoolExecutor() as executor:
            # 1) Tell each service to initialize (cache) this order
            logger.info(f"[Order {order_id}] - Initializing service caches")

            list(executor.map(
                lambda f: f(request_data, order_id),
                [initialize_fraud_detection, initialize_transaction_verification, initialize_suggestions]
            ))

            # 2) Verify order items (a) and ensure that the user data is filled (b)
            verify_order_items_future = executor.submit(verify_order_items, order_id)
            verify_user_data_future = executor.submit(verify_user_data, order_id)

            # 3) Verify credit card data (c) after (a) and check user data for fraud (d) after (b)
            verify_credit_card_future = executor.submit(verify_credit_card, order_id, verify_order_items_future)
            check_user_data_future = executor.submit(check_user_data, order_id, verify_user_data_future)

            # 4) Check credit card for fraud (e) after (c) and (d)
            verify_credit_card_future.result()
            check_user_data_future.result()

            check_credit_card(order_id)

            # 5) Get book suggestions (f) after (e)
            books = get_book_suggestions(order_id)

            return {
                "orderId": order_id,
                "status": "Order Approved",
                "suggestedBooks": [{"bookId": book.book_id, "title": book.title, "author": book.author} for book in books]
            }, 200
    
    except Exception as error:
        # Order related errors
        if error.args[0] == order_id:
            logger.info(f"[Order {order_id}] - {error.args[1]}")
            return {
                "orderId": order_id,
                "status": "Order Rejected",
                "suggestedBooks": []
            }
        
        # Other errors
        else:
            logger.error(f"[Order {order_id}] - An error occurred: {error.args[0]}")
            return {
                "error": {
                    "code": 500,
                    "message": "An error occurred"
                }
            }, 500
    
    finally:
        logger.info(f"[Order {order_id}] - Clearing service caches")
        
        with futures.ThreadPoolExecutor() as executor:
            list(executor.map(
                lambda f: f(order_id),
                [clear_fraud_detection, clear_transaction_verification, clear_suggestions]
            ))

        logger.info(f"[Order {order_id}] - Checkout request completed")

if __name__ == '__main__':
    # Run the app in debug mode to enable hot reloading.
    # This is useful for development.
    # The default port is 5000.
    app.run(host='0.0.0.0')
