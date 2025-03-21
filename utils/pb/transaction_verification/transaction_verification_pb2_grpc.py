# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
import transaction_verification_pb2 as transaction__verification__pb2


class TransactionVerificationServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.InitOrder = channel.unary_unary(
                '/transaction_verification.TransactionVerificationService/InitOrder',
                request_serializer=transaction__verification__pb2.InitializationRequest.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )
        self.VerifyItems = channel.unary_unary(
                '/transaction_verification.TransactionVerificationService/VerifyItems',
                request_serializer=transaction__verification__pb2.ContinuationRequest.SerializeToString,
                response_deserializer=transaction__verification__pb2.VerificationResponse.FromString,
                )
        self.VerifyUserData = channel.unary_unary(
                '/transaction_verification.TransactionVerificationService/VerifyUserData',
                request_serializer=transaction__verification__pb2.ContinuationRequest.SerializeToString,
                response_deserializer=transaction__verification__pb2.VerificationResponse.FromString,
                )
        self.VerifyCreditCard = channel.unary_unary(
                '/transaction_verification.TransactionVerificationService/VerifyCreditCard',
                request_serializer=transaction__verification__pb2.ContinuationRequest.SerializeToString,
                response_deserializer=transaction__verification__pb2.VerificationResponse.FromString,
                )


class TransactionVerificationServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def InitOrder(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def VerifyItems(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def VerifyUserData(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def VerifyCreditCard(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_TransactionVerificationServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'InitOrder': grpc.unary_unary_rpc_method_handler(
                    servicer.InitOrder,
                    request_deserializer=transaction__verification__pb2.InitializationRequest.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'VerifyItems': grpc.unary_unary_rpc_method_handler(
                    servicer.VerifyItems,
                    request_deserializer=transaction__verification__pb2.ContinuationRequest.FromString,
                    response_serializer=transaction__verification__pb2.VerificationResponse.SerializeToString,
            ),
            'VerifyUserData': grpc.unary_unary_rpc_method_handler(
                    servicer.VerifyUserData,
                    request_deserializer=transaction__verification__pb2.ContinuationRequest.FromString,
                    response_serializer=transaction__verification__pb2.VerificationResponse.SerializeToString,
            ),
            'VerifyCreditCard': grpc.unary_unary_rpc_method_handler(
                    servicer.VerifyCreditCard,
                    request_deserializer=transaction__verification__pb2.ContinuationRequest.FromString,
                    response_serializer=transaction__verification__pb2.VerificationResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'transaction_verification.TransactionVerificationService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class TransactionVerificationService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def InitOrder(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/transaction_verification.TransactionVerificationService/InitOrder',
            transaction__verification__pb2.InitializationRequest.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def VerifyItems(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/transaction_verification.TransactionVerificationService/VerifyItems',
            transaction__verification__pb2.ContinuationRequest.SerializeToString,
            transaction__verification__pb2.VerificationResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def VerifyUserData(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/transaction_verification.TransactionVerificationService/VerifyUserData',
            transaction__verification__pb2.ContinuationRequest.SerializeToString,
            transaction__verification__pb2.VerificationResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def VerifyCreditCard(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/transaction_verification.TransactionVerificationService/VerifyCreditCard',
            transaction__verification__pb2.ContinuationRequest.SerializeToString,
            transaction__verification__pb2.VerificationResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
