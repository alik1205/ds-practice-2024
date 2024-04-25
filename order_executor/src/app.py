import sys
import os
import logging
from concurrent import futures
import grpc
import uuid

FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path_order_queue = os.path.abspath(os.path.join(FILE, '../../../utils/pb/order_queue'))
utils_path_order_executor = os.path.abspath(os.path.join(FILE, '../../../utils/pb/order_executor'))
sys.path.insert(0, utils_path_order_queue)
sys.path.insert(1, utils_path_order_executor)

import order_queue_pb2 as order_queue
import order_queue_pb2_grpc as order_queue_grpc

import order_executor_pb2 as order_executor
import order_executor_pb2_grpc as order_executor_grpc

logger = logging.getLogger(__name__)
stdout = logging.StreamHandler(stream=sys.stdout)

fmt = logging.Formatter("%(message)s")

class OrderExecutor(order_executor_grpc.OrderExecutorServicer):
    def __init__(self, id, next_instance, order_queue_channel):
        self.id = id
        self.next_instance = next_instance
        self.leader = None
        self.order_queue_stub = order_queue_grpc.OrderQueueStub(order_queue_channel)

    # checking stock
    def check_stock(self, item_id, quantity):
        # Check if the item is in stock
        # for now we don't have database, so we will return True
        return True

    def start_election(self):
        # Start an election
        self.send_election_message(self.id)

    def send_election_message(self, id):
        # Send an election message to the next instance
        self.next_instance.receive_election_message(id)

    def receive_election_message(self, id):
        # Receive an election message
        if id > self.id:
            # If the ID in the message is higher, forward the message
            self.send_election_message(id)
        elif id < self.id:
            # If our own ID is higher, start a new election
            self.start_election()
        else:
            # If the ID in the message is our own ID, we are the leader
            self.leader = self.id

    def dequeue_order(self):
        # Only the leader can dequeue orders
        if self.leader == self.id:
            # Send a request to the order_queue service to dequeue an order
            request = order_queue.DequeueRequest()
            response = self.order_queue_stub.DequeueOrder(request)
            if response.Dequeued:
                logger.info(f"Order {response.orderId} is being executed...")
                return response.orderId
        return None

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Create a gRPC channel to the order_queue service
    order_queue_channel = grpc.insecure_channel('localhost:50054')
    # Define the number of OrderExecutor instances you want to create
    num_instances = 5  # Change this to the number of instances 
    # Create a list to hold your OrderExecutor instances
    order_executors = []
    # Create OrderExecutor instances
    for i in range(num_instances):
        order_executors.append(OrderExecutor(str(uuid.uuid4()), None, order_queue_channel))
    # Set the next_instance for each OrderExecutor
    for i in range(num_instances):
        order_executors[i].next_instance = order_executors[(i + 1) % num_instances]
    # Add OrderExecutor services to the server
    for executor in order_executors:
        order_executor_grpc.add_OrderExecutorServicer_to_server(executor, server)

    # Listen on port 50055
    port = "50055"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    print(f"Server started. Listening on port {port}.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
