import sys
import os
import logging

FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/transaction_verification'))
sys.path.insert(0, utils_path)
import transaction_verification_pb2 as transaction_verification
import transaction_verification_pb2_grpc as transaction_verification_grpc

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

def initialize_vector_clock(response):
    events_order = ['TV-items', 'TV-user_data', 'FD-user_data', 'TV-credit_card', 'FD-credit_card', 'S-books']
    for event in events_order:
        response.vectorClock.events[event] = 0
    logger.info("Transaction Verification Vector Clock is initialized")
    return response



class TransactionVerification(transaction_verification_grpc.TransactionVerificationServicer):
    def VerificationItems(self, request, context):
        response = transaction_verification.VerificationResponse()
        logger.info("Running Transaction Verification Items for order %s", request.orderId)
        response = initialize_vector_clock(response)
        response.vectorClock.events['TV-items'] += 1
        response.verified = True
        return response
    
    def VerificationUser(self, request, context):
        response = transaction_verification.VerificationResponse()
        logger.info("Running Transaction Verification User for order %s", request.orderId)
        response = initialize_vector_clock(response)
        response.vectorClock.events['TV-user_data'] += 1
        response.verified = True
        return response
    
    def VerificationCreditCard(self, request, context):
        response = transaction_verification.VerificationResponse()
        logger.info("Running Transaction Verification Credit Card for order %s", request.orderId)

        response = initialize_vector_clock(response)
        response.vectorClock.events['TV-credit_card'] += 1

        if len(request.creditCard.number)!=5:
            response.verified =  False
        else:
            response.verified = True

        if response.verified:
            logger.info("Transaction verified successfuly.")
        else:
            logger.error("Transaction verification failed.")

        return response

def serve():

    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add TransactionVerification service
    transaction_verification_grpc.add_TransactionVerificationServicer_to_server(TransactionVerification(), server)
    # Listen on port 50052
    port = "50052"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    print(f"Server started. Listening on port {port}.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()