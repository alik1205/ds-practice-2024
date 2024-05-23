import sys
import os
import logging
import json

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

# DATABASE_FILE = '../../book_database.json'
DATABASE_FILE = os.path.abspath(os.path.join(FILE, '../../../book_database.json'))
print(DATABASE_FILE)
try:
    with open(DATABASE_FILE, 'r') as f:
        data = json.load(f)
        print("no error")
        logger.info("Reading Book Database.")
except FileNotFoundError:
    logger.info("Error reading Book Database.")
    print("error")
    data = {}

class BooksDatabaseServicer(database_grpc.BooksDatabaseServicer):
    def Prepare(self, request, context):
        response = database.PrepareResponse()
        logger.info("Prepare Database for an update.")
        response.success = True
        return response

    def Read(self, request, context):       
        logger.info("Recived read request.")
        if request.key in data:
            logger.info(f"{request.key}:{data[request.key]}")
            return database.ReadResponse(value=data[request.key])
        else:
            logger.info(f"There is no such book in Book Database: {request.key}")
            return database.ReadResponse(value=0)

    def Write(self, request, context):
        logger.info("Recived write request.")
        logger.info(f"Key: {request.key}\nValue: {request.value}")
        data[request.key] = request.value
        with open(DATABASE_FILE, 'w') as f:
            json.dump(data, f)
        return database.WriteResponse(success=True)

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add Suggestions service
    database_grpc.add_BooksDatabaseServicer_to_server(BooksDatabaseServicer(), server)
    # Listen on port 50053
    ports = ["50055", "50056", "50057"]
    for port in ports:
        server.add_insecure_port("[::]:" + port)
        print(f"Server started. Listening on port {port}.")
    # Start the server
    server.start()
    print(f"Server started. Listening on port {port}.")
    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()