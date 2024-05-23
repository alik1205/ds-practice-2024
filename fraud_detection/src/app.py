import sys
import os
import logging

FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/fraud_detection'))
sys.path.insert(0, utils_path)
import fraud_detection_pb2 as fraud_detection
import fraud_detection_pb2_grpc as fraud_detection_grpc

import grpc
from concurrent import futures

logger = logging.getLogger(__name__)
stdout = logging.StreamHandler(stream=sys.stdout)

fmt = logging.Formatter(
    "%(message)s"
)

stdout.setFormatter(fmt)
logger.addHandler(stdout)
logger.setLevel(logging.INFO)

# OpenTelemetry imports
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource


resource = Resource(attributes={
    SERVICE_NAME: "fraud_detection"
})

print("NAME: ", __name__)

# OpenTelemetry setup
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
span_exporter = OTLPSpanExporter(endpoint="observability:4317", insecure=True)
span_processor = BatchSpanProcessor(span_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

metric_exporter = OTLPMetricExporter(endpoint="observability:4317", insecure=True)
reader = PeriodicExportingMetricReader(exporter=metric_exporter)
meter_provider = MeterProvider(metric_readers=[reader])
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter(__name__)

# Example metrics
counter = meter.create_counter("requests_counter", description="Counts the number of requests")
histogram = meter.create_histogram("request_duration", description="Records the duration of requests")


def initialize_vector_clock(response):
    events_order = ['TV-items', 'TV-user_data', 'FD-user_data', 'TV-credit_card', 'FD-credit_card', 'S-books']
    for event in events_order:
        response.vectorClock.events[event] = 0
    logger.info("Fraud Detection Vector Clock is initialized")
    return response

class FraudDetection(fraud_detection_grpc.FraudDetectionServicer):
    def DetectionUser(self, request, context):
        with tracer.start_as_current_span("DetectionUser") as span:
            response = fraud_detection.DetectionResponse()
            logger.info("Running Fraud DetectionUser for order %s", request.orderId)

            span.set_attribute("order.id", request.orderId)
            counter.add(1, {"method": "DetectionUser"})

            response = initialize_vector_clock(response)
            response.vectorClock.events['FD-user_data'] += 1

            response.detected = False

            #checking if name is longer than 2 letters
            if len(request.user.name) <= 2:
                response.detected = True
                logger.error("User name should be longer than 1 letter.")
                return response
            
            #checking user has name 'Fraud Master'
            if request.user.name == "Fraud Master":
                response.detected = True
                logger.error("User with name 'Fraud Master' detected.")
            
            #checking if contact information (phone, or email, etc) is longer than 6 characters
            if len(request.user.contact) <= 5:
                response.detected = True
                logger.error("User contact information should be longer than 5 characters.")
                return response

            if not response.detected:
                logger.info("No fraud detected.")
            else:
                logger.error("Fraud detected.")
            
            return response
    
    def DetectionCreditCard(self, request, context):
        with tracer.start_as_current_span("DetectionCreditCard") as span:
            response = fraud_detection.DetectionResponse()
            logger.info("Running Fraud DetectCreditCard for order %s", request.orderId)

            span.set_attribute("order.id", request.orderId)
            counter.add(1, {"method": "DetectionCreditCard"})

            response = initialize_vector_clock(response)
            response.vectorClock.events['FD-credit_card'] += 1
            response.detected = False
            return response

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add FraudDetection service
    fraud_detection_grpc.add_FraudDetectionServicer_to_server(FraudDetection(), server)
    # Listen on port 50051
    port = "50051"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    print(f"Server started. Listening on port {port}.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()