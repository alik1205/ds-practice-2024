import sys
import os
import logging

FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/database'))
sys.path.insert(0, utils_path)
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

data = {
    'Learning Python': 3,
}

class BooksDatabaseServicer(database_grpc.BooksDatabaseServicer):
    def Read(self, request, context):
        if request.key in data:
            return database.ReadResponse(value=data[request.key])
        else:
            return database.ReadResponse(value="")

    def Write(self, request, context):
        data[request.key] = request.value
        return database.WriteResponse(success=True)

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add Suggestions service
    database_grpc.add_BooksDatabaseServicer_to_server(BooksDatabaseServicer(), server)
    # Listen on port 50053
    port = "50055"
    server.add_insecure_port("[::]:" + port)
    # Start the server
    server.start()
    print(f"Server started. Listening on port {port}.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()