import sys
import os
import threading
import uuid
import logging
import random

FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path_fraud_detection = os.path.abspath(os.path.join(FILE, '../../../utils/pb/fraud_detection'))
utils_path_transaction_verification = os.path.abspath(os.path.join(FILE, '../../../utils/pb/transaction_verification'))
utils_path_suggestions = os.path.abspath(os.path.join(FILE, '../../../utils/pb/suggestions'))
utils_path_order_queue = os.path.abspath(os.path.join(FILE, '../../../utils/pb/order_queue'))
utils_path_order_executor = os.path.abspath(os.path.join(FILE, '../../../utils/pb/order_executor'))

sys.path.insert(0, utils_path_fraud_detection)
sys.path.insert(1, utils_path_transaction_verification)
sys.path.insert(2, utils_path_suggestions)
sys.path.insert(3, utils_path_order_queue)
sys.path.insert(4, utils_path_order_executor)

import fraud_detection_pb2 as fraud_detection
import fraud_detection_pb2_grpc as fraud_detection_grpc

import transaction_verification_pb2 as transaction_verification
import transaction_verification_pb2_grpc as transaction_verification_grpc

import suggestions_pb2 as suggestions
import suggestions_pb2_grpc as suggestions_grpc

import order_queue_pb2 as order_queue
import order_queue_pb2_grpc as order_queue_grpc

import order_executor_pb2 as order_executor
import order_executor_pb2_grpc as order_executor_grpc

import grpc

from flask import Flask, request, jsonify
from flask_cors import CORS

logger = logging.getLogger(__name__)
stdout = logging.StreamHandler(stream=sys.stdout)

fmt = logging.Formatter(
    "%(message)s"
)

stdout.setFormatter(fmt)
logger.addHandler(stdout)
logger.setLevel(logging.INFO)

# Create a simple Flask app.
app = Flask(__name__)
# Enable CORS for the app.
CORS(app)

def update_vector_clock(new_vc):
    global vector_clock
    events_order = ['TV-items', 'TV-user_data', 'FD-user_data', 'TV-credit_card', 'FD-credit_card', 'S-books']
    for event in events_order:
        vector_clock[event]+=new_vc[event]
    logger.info("Vector Clock is updated: %s", vector_clock)

def leader_election(replicas):
    return random.choice(replicas)


def FraudDetection(events, request, order_id):
    with grpc.insecure_channel('fraud_detection:50051') as channel:
        stub = fraud_detection_grpc.FraudDetectionStub(channel)

        response = fraud_detection.DetectionResponse()

        done = events['TV-user_data'].wait(1)
        if done:
            done = False
            user = fraud_detection.User(
                name=request['user']['name'],
                contact=request['user']['contact']
                )
            response = stub.DetectionUser(fraud_detection.DURequest(orderId=order_id, user=user))
            update_vector_clock(response.vectorClock.events)
            if not response.detected:
                events['FD-user_data'].set()
            else:
                return response
        else:
            response.detected = True
            return response
        
        done = events['TV-credit_card'].wait(10)
        if done:
            creditCard = fraud_detection.CreditCard(
                number=request['creditCard']['number'],
                expirationDate=request['creditCard']['expirationDate'],
                cvv=request['creditCard']['cvv']
                )
            response = stub.DetectionCreditCard(fraud_detection.DCCRequest(orderId=order_id, creditCard=creditCard))
            update_vector_clock(response.vectorClock.events)
            if not response.detected:
                events['FD-credit_card'].set()
            else:
                return response
        else:
            response.detected = True
            return response
        
    return response

def TransactionVerification(events, request, order_id):
    with grpc.insecure_channel('transaction_verification:50052') as channel:
        stub = transaction_verification_grpc.TransactionVerificationStub(channel)

        response = transaction_verification.VerificationResponse()

        items = list()
        for _item in request["items"]:
            item = transaction_verification.Item()
            item.name = _item["name"]
            item.quantity = _item["quantity"]
            items.append(item)
        response = stub.VerificationItems(transaction_verification.VIRequest(orderId=order_id, items=items))
        update_vector_clock(response.vectorClock.events)
        if response.verified:
            events['TV-items'].set()
        else:
            return response
        
        user = transaction_verification.User(
            name=request['user']['name'],
            contact=request['user']['contact']
            )
        response = stub.VerificationUser(transaction_verification.VURequest(orderId=order_id, user=user))
        update_vector_clock(response.vectorClock.events)
        if response.verified:
            events['TV-user_data'].set()
        else:
            return response
        
        done = events['FD-user_data'].wait(10)
        if done:
            creditCard = transaction_verification.CreditCard(
                number=request['creditCard']['number'],
                expirationDate=request['creditCard']['expirationDate'],
                cvv=request['creditCard']['cvv']
                )
            response = stub.VerificationCreditCard(transaction_verification.VCCRequest(orderId=order_id, creditCard=creditCard))
            update_vector_clock(response.vectorClock.events)
            if response.verified:
                events['TV-credit_card'].set()
            else:
                return response
        else:
            response.verified = False
            return response

    return response

def SuggestionsService(events, request, order_id):
    with grpc.insecure_channel('suggestions:50053') as channel:
        stub = suggestions_grpc.SuggestionsServiceStub(channel)

        done = events['FD-credit_card'].wait(10)
        if done:
            items = list()
            for _item in request["items"]:
                item = suggestions.Item()
                item.name = _item["name"]
                item.quantity = _item["quantity"]
                items.append(item)
            response = stub.Suggestions(suggestions.SuggestionRequest(orderId=order_id, items=items))
            update_vector_clock(response.vectorClock.events)
        else:
            return None
    return response

def QueueService(action, order_id):
    with grpc.insecure_channel('order_queue:50054') as channel:
        stub = order_queue_grpc.OrderQueueStub(channel)

        if action == "ENQUEUE":
            response = stub.EnqueueOrder(order_queue.EnqueueRequest(orderId=order_id))
        elif action == "DEQUEUE":
            response = stub.DequeueOrder(order_queue.DequeueRequest())

    return response

def ExecutorService(order_id, request):
    replicas = ["order_executor1:50058", "order_executor2:50059"]
    with grpc.insecure_channel(leader_election(replicas)) as channel:
        stub = order_executor_grpc.OrderExecutorStub(channel)

        items = list()
        for _item in request["items"]:
            item = order_executor.Item()
            item.name = _item["name"]
            item.quantity = _item["quantity"]
            items.append(item)

        response = stub.ExecuteOrder(order_executor.ExecuteOrderRequest(order_id=order_id, items=items))

    return response

def run_in_thread(func, args, result_dict, key):
    result_dict[key] = func(*args)

@app.route('/checkout', methods=['POST'])
def checkout():
    global vector_clock
    """
    Responds with a JSON object containing the order ID, status, and suggested books.
    """
    logger.info("Received checkout request: %s", request.json)

    # Generating unique order ID
    logger.info("Generating Order ID...")
    order_id = str(uuid.uuid4())
    logger.info("Order ID: %s", order_id)

    # Defining an event order
    events_order = ['TV-items', 'TV-user_data', 'FD-user_data', 'TV-credit_card', 'FD-credit_card', 'S-books']
    logger.info("Event Order: %s", events_order)

    # Initialize vector clock
    vector_clock = dict()
    for event in events_order:
        vector_clock[event] = 0
    logger.info("Vector Clock is initialized: %s", vector_clock)

    # Creating an event objects
    events = dict()
    for event in events_order:
        events[event] = threading.Event()

    # Initialising the threads
    results = {}

    fraud_detection_thread = threading.Thread(target=run_in_thread, args=(FraudDetection, (events, request.json, order_id), results, 'fraud_detection'))
    suggestions_thread = threading.Thread(target=run_in_thread, args=(SuggestionsService, (events, request.json, order_id), results, 'suggestions'))
    transaction_verification_thread = threading.Thread(target=run_in_thread, args=(TransactionVerification, (events, request.json, order_id), results, 'transaction_verification'))

    fraud_detection_thread.start()
    suggestions_thread.start()
    transaction_verification_thread.start()

    fraud_detection_thread.join()
    suggestions_thread.join()
    transaction_verification_thread.join()

    fraud_detection_response = results['fraud_detection']
    suggestions_response = results['suggestions']
    transaction_verification_response = results['transaction_verification']

    logger.info("Creating response...")
    response = {
        "orderId": order_id,  # Include generated OrderID in the response
        "status": 'Order Rejected',
        "suggestedBooks": []
    }

    if fraud_detection_response.detected or not transaction_verification_response.verified:
        response['status'] = 'Order Rejected'
        return jsonify(response)
    else:
        response['status'] = 'Order Accepted'

    if suggestions_response:
        for suggested_book in suggestions_response.suggestedBooks:
            book_dict = {
                "bookId": suggested_book.bookId,
                "title": suggested_book.title,
                "author": suggested_book.author
            }
            response["suggestedBooks"].append(book_dict)
    
    enqueue_responce = QueueService("ENQUEUE", order_id)
    if enqueue_responce.Enqueued:
        logger.info("Order %s is enqueued.", enqueue_responce.orderId)
        executor_responce = ExecutorService(order_id, request.json)

    return jsonify(response)


if __name__ == '__main__':
    # The default port is 5000.
    app.run(host='0.0.0.0', debug=True)
