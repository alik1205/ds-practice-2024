import sys
import os
import threading
import uuid
import logging

FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
utils_path_fraud_detection = os.path.abspath(os.path.join(FILE, '../../../utils/pb/fraud_detection'))
utils_path_transaction_verification = os.path.abspath(os.path.join(FILE, '../../../utils/pb/transaction_verification'))
utils_path_suggestions = os.path.abspath(os.path.join(FILE, '../../../utils/pb/suggestions'))

sys.path.insert(0, utils_path_fraud_detection)
sys.path.insert(1, utils_path_transaction_verification)
sys.path.insert(2, utils_path_suggestions)

import fraud_detection_pb2 as fraud_detection
import fraud_detection_pb2_grpc as fraud_detection_grpc

import transaction_verification_pb2 as transaction_verification
import transaction_verification_pb2_grpc as transaction_verification_grpc

import suggestions_pb2 as suggestions
import suggestions_pb2_grpc as suggestions_grpc

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

def FraudDetection(request, order_id):
    with grpc.insecure_channel('fraud_detection:50051') as channel:
        stub = fraud_detection_grpc.FraudDetectionStub(channel)

        user = fraud_detection.User(
            name=request['user']['name'],
            contact=request['user']['contact']
            )
        billingAddress = fraud_detection.BillingAddress(
            street=request['billingAddress']['street'],
            city=request['billingAddress']['city'],
            state=request['billingAddress']['state'],
            zip=request['billingAddress']['zip'],
            country=request['billingAddress']['country'],
            )
        response = stub.Detection(fraud_detection.DetectionRequest(orderId=order_id, user=user, billingAddress=billingAddress))
    return response

def TransactionVerification(request, order_id):
    with grpc.insecure_channel('transaction_verification:50052') as channel:
        stub = transaction_verification_grpc.TransactionVerificationStub(channel)

        creditCard = transaction_verification.CreditCard(
            number=request['creditCard']['number'],
            expirationDate=request['creditCard']['expirationDate'],
            cvv=request['creditCard']['cvv']
            )
        response = stub.Verification(transaction_verification.VerificationRequest(orderId=order_id, creditCard=creditCard))
    return response

def SuggestionsService(request, order_id):
    with grpc.insecure_channel('suggestions:50053') as channel:
        stub = suggestions_grpc.SuggestionsServiceStub(channel)

        items = list()
        for _item in request["items"]:
            item = suggestions.Item()
            item.name = _item["name"]
            item.quantity = _item["quantity"]
            items.append(item)
        response = stub.Suggestions(suggestions.SuggestionRequest(orderId=order_id, items=items))
    return response

def run_in_thread(func, args, result_dict, key):
    result_dict[key] = func(*args)

@app.route('/checkout', methods=['POST'])
def checkout():
    """
    Responds with a JSON object containing the order ID, status, and suggested books.
    """
    logger.info("Received checkout request: %s", request.json)

    logger.info("Generating Order ID...")
    order_id = str(uuid.uuid4())
    logger.info("Order ID: %s", order_id)

    results = {}

    fraud_detection_thread = threading.Thread(target=run_in_thread, args=(FraudDetection, (request.json, order_id), results, 'fraud_detection'))
    suggestions_thread = threading.Thread(target=run_in_thread, args=(SuggestionsService, (request.json, order_id), results, 'suggestions'))
    transaction_verification_thread = threading.Thread(target=run_in_thread, args=(TransactionVerification, (request.json, order_id), results, 'transaction_verification'))

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
        "status": '',
        "suggestedBooks": []
    }

    for suggested_book in suggestions_response.suggestedBooks:
        book_dict = {
            "bookId": suggested_book.bookId,
            "title": suggested_book.title,
            "author": suggested_book.author
        }
        response["suggestedBooks"].append(book_dict)

    if fraud_detection_response.detected or not transaction_verification_response.verified:
        response['status'] = 'Order Rejected'
    else:
        response['status'] = 'Order Accepted'

    return jsonify(response)


if __name__ == '__main__':
    # The default port is 5000.
    app.run(host='0.0.0.0', debug=True)