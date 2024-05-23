import sys
import os
import logging

FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/payment'))
sys.path.insert(0, utils_path)
import payment_pb2 as payment
import payment_pb2_grpc as payment_grpc

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


class Payment(payment_grpc.PaymentSystemServicer):
    def Prepare(self, request, context):
        response = payment.PrepareResponse()
        logger.info("Prepare Payment for order %s", request.order_id)
        response.success = True
        return response
    
    def ExecutePayment(self, request, context):
        response = payment.PaymentResponse()
        logger.info("Execute Payment for order %s", request.order_id)
        response.success = True
        return response

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add Suggestions service
    payment_grpc.add_PaymentSystemServicer_to_server(Payment(), server)
    # Listen on port 50053
    port = "50060"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    print(f"Server started. Listening on port {port}.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()