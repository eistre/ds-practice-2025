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

from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

resource = Resource.create(attributes={"service.name": "payment-service"})

# Traces
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)
span_processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://observability:4318/v1/traces"))
trace.get_tracer_provider().add_span_processor(span_processor)

# Metrics
reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint="http://observability:4318/v1/metrics"))
metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[reader]))
meter = metrics.get_meter(__name__)

# Counter
payment_counter = meter.create_counter("payment_requests", description="Total payment attempts")
success_counter = meter.create_counter("payment_success", description="Total successful payments")
abort_counter = meter.create_counter("payment_failed", description="Total failed payments")

# UpDownCounter (can go up or down)
payment_in_progress = meter.create_up_down_counter(
    "payment_in_progress",
    description="Number of payments currently in progress"
)

#Histogram
payment_amount_histogram = meter.create_histogram(
    "payment_amount",
    description="Histogram of payment amounts"
)


import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] - [%(levelname)s] - [Payment] - [Thread %(thread)d] - %(message)s"
)

logger = logging.getLogger()

class PaymentService(payment_pb2_grpc.PaymentService):
    def __init__(self):
        self.prepared_payments = {}
        PaymentService._instance = self
    
    def Prepare(self, request, context):
        with tracer.start_as_current_span("Prepare Payment") as span:
            span.set_attribute("order_id", request.order_id)
            span.set_attribute("amount", request.amount)
            payment_counter.add(1)
            payment_in_progress.add(1)
            #payment_amount_histogram.record(request.amount)
            # Dummy version: if amount is small then approved (person likely has enough to pay) with higher cost 70% approval
            approved = request.amount < 100 or random.random()>0.3
            if approved:
                self.prepared_payments[request.order_id] = request.amount
                logger.info(f"[Order {request.order_id}] - Payment prepared for amount ${request.amount}")
                return payment_pb2.PrepareResponse(ready=True)

            logger.warning(f"[Order {request.order_id}] - Payment rejected for amount ${request.amount}")
            return payment_pb2.PrepareResponse(ready=False)
    
    def Commit(self, request, context):
        with tracer.start_as_current_span("Commit Payment") as span:
            span.set_attribute("order_id", request.order_id)
            span.set_attribute("amount", request.amount)
            success_counter.add(1)
            payment_in_progress.add(-1)
            payment_amount_histogram.record(request.amount)
            if request.order_id in self.prepared_payments:
                logger.info(f"[Order {request.order_id}] - Committing payment of ${self.prepared_payments[request.order_id]}")
                del self.prepared_payments[request.order_id]
                return payment_pb2.CommitResponse(success=True)
            
            logger.error(f"[Order {request.order_id}] - Commit failed, no prepared payment found")
            return payment_pb2.CommitResponse(success=False)
    
    def Abort(self, request, context):
        with tracer.start_as_current_span("Abort Payment") as span:
            span.set_attribute("order_id", request.order_id)
            span.set_attribute("amount", request.amount)
            abort_counter.add(1)
            payment_in_progress.add(-1)
            if request.order_id in self.prepared_payments:
                del self.prepared_payments[request.order_id]
                logger.info(f"[Order {request.order_id}] - Payment aborted for amount ${request.amount}")
                return payment_pb2.AbortResponse(aborted=True)

            logger.warning(f"[Order {request.order_id}] - Abort called, but no payment to abort")
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
