import sys
import os
import logging

FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/order_queue'))
sys.path.insert(0, utils_path)
import order_queue_pb2 as order_queue
import order_queue_pb2_grpc as order_queue_grpc

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

class OrderQueue(order_queue_grpc.OrderQueueServicer):
    def __init__(self):
        self.queue = []

    def EnqueueOrder(self, request, context):
        response = order_queue.EnqueueResponse()
        logger.info("Received EnqueueOrder request for order ID: %s", request.orderId)

        self.queue.append(request)

        response.orderId = request.orderId
        response.Enqueued = True

        return response
    
    def DequeueOrder(self, request, context):
        response = order_queue.DequeueResponse()
        logger.info("Received DequeueOrder request.")

        if not self.queue:
            logger.info("Queue is empty. Cannot dequeue.")
            response.Dequeued = False
            return response

        order = self.queue.pop(0)

        logger.info("Dequeue oreder ID: %s", order.orderId)

        response.orderId = order.orderId
        response.Dequeued = True
        
        return response

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add Suggestions service
    order_queue_grpc.add_OrderQueueServicer_to_server(OrderQueue(), server)
    # Listen on port 50053
    port = "50054"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    print(f"Server started. Listening on port {port}.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()