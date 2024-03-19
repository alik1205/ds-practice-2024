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

# logging.basicConfig(level=logging.NOTSET)
# logging.root.setLevel(logging.NOTSET)
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# c_handler = logging.StreamHandler()
# logger.addHandler(c_handler)
# logger.setLevel(logging.INFO)
logger = logging.getLogger(__name__)
stdout = logging.StreamHandler(stream=sys.stdout)

fmt = logging.Formatter(
    "%(message)s"
)

stdout.setFormatter(fmt)
logger.addHandler(stdout)
logger.setLevel(logging.INFO)

class FraudDetection(fraud_detection_grpc.FraudDetectionServicer):
    def Detection(self, request, context):
        response = fraud_detection.DetectionResponse()
        logger.info("Running Fraud Detection for order %s", request.orderId)

        if request.user.name == "Alex":
            response.detected = True
        else:
            response.detected = False

        if not response.detected:
            logger.info("No fraud detected.")
        else:
            logger.error("Fraud detected.")
        
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