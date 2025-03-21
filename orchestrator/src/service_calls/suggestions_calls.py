import sys
import os

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
sys.path.insert(0, os.path.abspath(os.path.join(FILE, f"../../../../utils/pb/suggestions")))

import grpc
import logging
import suggestions_pb2 as suggestions
import suggestions_pb2_grpc as suggestions_grpc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] - [%(levelname)s] - [Thread %(thread)d] - %(message)s"
)

logger = logging.getLogger()

def initialize_suggestions(request, order_id):
    with grpc.insecure_channel('suggestions:50053') as channel:
        stub = suggestions_grpc.SuggestionServiceStub(channel)
        stub.InitOrder(suggestions.InitializationRequest(
            order_id=order_id,
            items=[
                suggestions.Item(name=item["name"], quantity=item["quantity"]) for item in request["items"]
            ]
        ))

def get_book_suggestions(order_id):
    with grpc.insecure_channel('suggestions:50053') as channel:
        stub = suggestions_grpc.SuggestionServiceStub(channel)
        response: suggestions.SuggestionResponse = stub.SuggestBooks(suggestions.ContinuationRequest(order_id=order_id))

        logger.info(f"[Order {order_id}] - Suggested books: {[book.title for book in response.books]}")

        return response.books
