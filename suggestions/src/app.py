import sys
import os

FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
suggestions_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/suggestions'))
sys.path.insert(0, suggestions_grpc_path)

from suggestions_pb2 import *
from suggestions_pb2_grpc import *

import grpc
import datetime
from concurrent import futures

class SuggestionService(SuggestionServiceServicer):
    def __init__(self):
        print("Transaction verification service initialized")

    def getSuggestions(self, request: SuggestionRequest, _):
        print(f"Received request for suggestion for books {request.items}")
        
        book1 = Book(bookId="1", title="Book 1", author="Author A")
        book2 = Book(bookId="2", title="Book 2", author="Author B")
        
        # Adding books to the response
        response = SuggestionResponse(books=[book1, book2])
        return response


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
    print("Server started. Listening on port 50053.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()