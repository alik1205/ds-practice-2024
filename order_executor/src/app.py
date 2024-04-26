import sys
import os
import logging

FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/order_executor'))
utils_path_order_queue = os.path.abspath(os.path.join(FILE, '../../../utils/pb/order_queue'))
utils_path_database = os.path.abspath(os.path.join(FILE, '../../../utils/pb/database'))

sys.path.insert(0, utils_path)
sys.path.insert(1, utils_path_order_queue)
sys.path.insert(2, utils_path_database)


import order_executor_pb2 as order_executor
import order_executor_pb2_grpc as order_executor_grpc

import order_queue_pb2 as order_queue
import order_queue_pb2_grpc as order_queue_grpc

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



class OrderExecutorServicer(order_executor_grpc.OrderExecutorServicer):
    def ExecuteOrder(self, request, context):
        self.request = request
        response = order_executor.ExecuteOrderResponse()
        logger.info("Running Order Execution for order %s", request.order_id)
        success = self.DequeueOrder()
        if success:
            for item in request.items:
                read_responce = self.DatabaseService("READ", key=item.name)
                logger.info(f"Read Responce: {read_responce.value}")
                if read_responce.value:
                    write_responce = self.DatabaseService("WRITE", key=item.name, value=read_responce.value-item.quantity)

        response.success = True
        return response
    
    def DequeueOrder(self):
        with grpc.insecure_channel('order_queue:50054') as channel:
            stub = order_queue_grpc.OrderQueueStub(channel)
            response = stub.DequeueOrder(order_queue.DequeueRequest())
            if response.Dequeued:
                logger.info(f"Order {self.request.order_id} is dequeued.")
            return response.Dequeued
    
    def DatabaseService(self, action, key, value=""):
        replicas = ['database2:50055', 'database2:50056', 'database3:50057']
        for replica in replicas:
            try:
                channel = grpc.insecure_channel(replica)
                stub = database_grpc.BooksDatabaseStub(channel)
                logger.info(f"Connected to replica {replica}.")

                if action == "WRITE":
                    response = stub.Write(database.WriteRequest(key=key, value=value))
                elif action == "READ":
                    response = stub.Read(database.ReadRequest(key=key))

                return response
            except:
                logger.info(f"Failed to connect to replica {replica}.")
                continue

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