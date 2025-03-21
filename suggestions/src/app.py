import sys
import os

FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
suggestions_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/suggestions'))
sys.path.insert(0, suggestions_grpc_path)

from suggestions_pb2 import *
from suggestions_pb2_grpc import *

import grpc
import json
import random
import logging
from google import genai
from concurrent import futures
from pydantic import BaseModel
from google.protobuf import empty_pb2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] - [%(levelname)s] - [Suggestions] - [Thread %(thread)d] - %(message)s"
)

logger = logging.getLogger()

class BookModel(BaseModel):
    title: str
    author: str

class AIResponse(BaseModel):
    suggested_books: list[BookModel]

AI_SUGGESTION_PROMPT = """
    You are an expert book recommendation system with knowledge in books and their authors.
    Analyze the given order details and suggest **5** books based on user interests and purchasing behavior.
    Even if you determine the order is used as test data, provide actual book recommendations to demonstrate your expertise.

    Consider these key factors:
    1. Ordered items (book names and quantities) - identify common themes or genres
    2. Popular books related to the purchased ones
    3. Trends in book recommendations

    Based on your expert analysis, suggest **5** books that the user may find interesting. Return:
    a list of suggested books.

    Respond only in valid JSON format with this structure:
    {
        "suggestedBooks": [
            {
                "title": "string",
                "author": "string"
            }
        ]
    }

    Here are the books the user purchased:

"""

class SuggestionService(SuggestionServiceServicer):
    def __init__(self):
        # Initialize google genai client
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        self.orders: dict[str, InitializationRequest] = {}
        logger.info("Suggestion service initialized")

    def InitOrder(self, request: InitializationRequest, _):
        self.orders[request.order_id] = request
        logger.info(f"[Order {request.order_id}] - Order initialized")
        return empty_pb2.Empty()

    def SuggestBooks(self, request: ContinuationRequest, _):
        logger.info(f"[Order {request.order_id}] - Book suggestion request received")

        # Check if the order exists
        if request.order_id not in self.orders:
            logger.info(f"[Order {request.order_id}] - Order not found: book suggestion failed")
            return SuggestionResponse(books=[])
        
        items = self.orders[request.order_id].items

        # Generate AI response
        ai_response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=AI_SUGGESTION_PROMPT + json.dumps({
                "items": [
                    {"name": item.name, "quantity": item.quantity} for item in items
                ]
            }),
            config={
                "response_mime_type": "application/json",
                "response_schema": AIResponse,
                "candidate_count": 1
            }
        )

        # Parse AI response
        ai_response: AIResponse = ai_response.parsed
        logger.info(f"[Order {request.order_id}] - Book suggestion successful: {[book.title for book in ai_response.suggested_books]}")

        return SuggestionResponse(
            books = [
                Book(book_id=str(random.randint(3, 100)), title=book.title, author=book.author) for book in ai_response.suggested_books
            ]
        )

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add the fraud detection service to the server
    add_SuggestionServiceServicer_to_server(SuggestionService(), server)
    # Listen on port 50053
    port = "50053"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    logger.info("Server started. Listening on port 50053.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
