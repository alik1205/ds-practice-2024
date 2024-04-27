import sys
import os
import logging

FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/order_executor'))
utils_path_order_queue = os.path.abspath(os.path.join(FILE, '../../../utils/pb/order_queue'))
utils_path_database = os.path.abspath(os.path.join(FILE, '../../../utils/pb/database'))
utils_path_payment = os.path.abspath(os.path.join(FILE, '../../../utils/pb/payment'))


sys.path.insert(0, utils_path)
sys.path.insert(1, utils_path_order_queue)
sys.path.insert(2, utils_path_database)
sys.path.insert(3, utils_path_payment)


import order_executor_pb2 as order_executor
import order_executor_pb2_grpc as order_executor_grpc

import order_queue_pb2 as order_queue
import order_queue_pb2_grpc as order_queue_grpc

import database_pb2 as database
import database_pb2_grpc as database_grpc

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



class OrderExecutorServicer(order_executor_grpc.OrderExecutorServicer):
    def ExecuteOrder(self, request, context):
        self.request = request
        
        replicas = ['database1:50055', 'database2:50056', 'database3:50057']
        for replica in replicas:
            try:
                self.database_stub = database_grpc.BooksDatabaseStub(grpc.insecure_channel(replica))
                logger.info(f"Connecting to replica {replica}.")
                break
            except:
                logger.info(f"Failed to connect to replica {replica}.")
                continue
        self.payment_stub = payment_grpc.PaymentSystemStub(grpc.insecure_channel('payment:50060'))

        response = order_executor.ExecuteOrderResponse()
        logger.info("Running Order Execution for order %s", request.order_id)
        success = self.DequeueOrder()
        if success:
            prepare_response_db = self.database_stub.Prepare(database.PrepareRequest(order_id=request.order_id))
            prepare_response_payment = self.payment_stub.Prepare(payment.PrepareRequest(order_id=request.order_id))
            if prepare_response_db.success and prepare_response_payment.success:
                execute_payment_response = self.payment_stub.ExecutePayment(payment.PaymentRequest(order_id=request.order_id, amount=20))
                for item in request.items:
                    read_responce = self.database_stub.Read(database.ReadRequest(key=item.name))
                    logger.info(f"Read Responce: {read_responce.value}")
                    if read_responce.value:
                        write_response = self.database_stub.Write(database.WriteRequest(key=item.name, value=read_responce.value-item.quantity))

        response.success = True
        return response
    
    def DequeueOrder(self):
        with grpc.insecure_channel('order_queue:50054') as channel:
            stub = order_queue_grpc.OrderQueueStub(channel)
            response = stub.DequeueOrder(order_queue.DequeueRequest())
            if response.Dequeued:
                logger.info(f"Order {self.request.order_id} is dequeued.")
        return response.Dequeued

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add TransactionVerification service
    order_executor_grpc.add_OrderExecutorServicer_to_server(OrderExecutorServicer(), server)
    # Listen on port 50052
    port1 = "50058"
    port2 = "50059"
    server.add_insecure_port("[::]:" + port1)
    server.add_insecure_port("[::]:" + port2)
    # Start the server
    server.start()
    print(f"Server started. Listening on port {port1}, {port2}.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()