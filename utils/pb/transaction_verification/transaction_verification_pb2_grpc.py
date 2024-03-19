# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import transaction_verification_pb2 as transaction__verification__pb2


class TransactionVerificationStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Verification = channel.unary_unary(
                '/transaction_verification.TransactionVerification/Verification',
                request_serializer=transaction__verification__pb2.VerificationRequest.SerializeToString,
                response_deserializer=transaction__verification__pb2.VerificationResponse.FromString,
                )


class TransactionVerificationServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Verification(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_TransactionVerificationServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Verification': grpc.unary_unary_rpc_method_handler(
                    servicer.Verification,
                    request_deserializer=transaction__verification__pb2.VerificationRequest.FromString,
                    response_serializer=transaction__verification__pb2.VerificationResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'transaction_verification.TransactionVerification', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class TransactionVerification(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Verification(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/transaction_verification.TransactionVerification/Verification',
            transaction__verification__pb2.VerificationRequest.SerializeToString,
            transaction__verification__pb2.VerificationResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)