import random
import sys
import os

FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
payment_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb'))
sys.path.insert(0, payment_grpc_path)

import grpc
from concurrent import futures
from utils.utils_pb2 import *
from payment.payment_pb2 import *
from payment.payment_pb2_grpc import *
from payment import payment_pb2_grpc
from payment import payment_pb2

import logging
logger = logging.getLogger()

class PaymentService(payment_pb2_grpc.PaymentService):
    def __init__(self):
        self.prepared_payments = {}
    
    def Prepare(self, request, context):
        # Dummy version: if amount is small then approved (person likely has enough to pay) with higher cost 70% approval
        approved = request.amount < 100 or random.random()>0.3
        if approved:
            self.prepared_payments[request.order_id] = request.amount
            print(f"Payment: Prepared for order {request.order_id} with amount ${request.amount}")
            return payment_pb2.PrepareResponse(ready=True)

        print(f"Payment: Rejected payment for order {request.order_id}, amount ${request.amount}")
        return payment_pb2.PrepareResponse(ready=False)
    
    def Commit(self, request, context):
        if request.order_id in self.prepared_payments:
            print(f"Payment: Payment committed for order {request.order_id}, amount ${self.prepared_payments[request.order_id]}")
            del self.prepared_payments[request.order_id]
            return payment_pb2.CommitResponse(success=True)
        
        print(f"Payment: Commit failed, no prepared payment for order {request.order_id}")
        return payment_pb2.CommitResponse(success=False)
    
    def Abort(self, request, context):
        if request.order_id in self.prepared_payments:
            del self.prepared_payments[request.order_id]
            print(f"Payment: Payment aborted for order {request.order_id}")
            return payment_pb2.AbortResponse(aborted=True)

        print(f"Payment: Abort called, but no payment to abort for order {request.order_id}")
        return payment_pb2.AbortResponse(aborted=False)
    
def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add the fraud detection service to the server
    add_PaymentServiceServicer_to_server(PaymentService(), server)
    # Listen on port 50057
    port = "50057"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    logger.info("Server started. Listening on port 50057.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
