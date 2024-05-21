import sys
import os
import logging
import re
from datetime import datetime
import json

FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")

utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/transaction_verification'))
utils_path_database = os.path.abspath(os.path.join(FILE, '../../../utils/pb/database'))

sys.path.insert(0, utils_path)
sys.path.insert(1, utils_path_database)

import transaction_verification_pb2 as transaction_verification
import transaction_verification_pb2_grpc as transaction_verification_grpc

import database_pb2 as database
import database_pb2_grpc as database_grpc


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
        replicas = ['database1:50055', 'database2:50056', 'database3:50057']
        for replica in replicas:
            try:
                self.database_stub = database_grpc.BooksDatabaseStub(grpc.insecure_channel(replica))
                logger.info(f"Connecting to replica {replica}.")
                break
            except:
                logger.info(f"Failed to connect to replica {replica}.")
                continue
        for item in request.items:
            read_responce = self.database_stub.Read(database.ReadRequest(key=item.name))
            if read_responce.value == 0: 
                logger.error(f"Item verification failed.")
                response.verified = False
                break
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

        response.verified = True
        
        #checking if credit card number is exactly 16 digits
        if len(request.creditCard.number)!=16:
            response.verified =  False
            logger.error("Credit card number should be exactly 16 digits.")
        
        #checking if expiry date is in format MM/YY
        if not re.match(r"^(0[1-9]|1[0-2])\/[0-9]{2}$", request.creditCard.expirationDate):
            response.verified = False
            logger.error("Expiration date should be in the format MM/YY.")
            return response
        
        #checking if expiration date is in the future
        exp_date = datetime.strptime(request.creditCard.expirationDate, "%m/%y")
        if exp_date <= datetime.now():
            response.verified = False
            logger.error("Expiration date should be in the future.")
            return response
        
        #checking if CVV is a 3-digit number
        if not re.match(r"^[0-9]{3}$", request.creditCard.cvv):
            response.verified = False
            logger.error("CVV should be a 3-digit number.")
            return response

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