# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from suggestions import suggestions_pb2 as suggestions_dot_suggestions__pb2
from utils import utils_pb2 as utils_dot_utils__pb2


class SuggestionServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.InitOrder = channel.unary_unary(
                '/suggestions.SuggestionService/InitOrder',
                request_serializer=suggestions_dot_suggestions__pb2.InitializationRequest.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )
        self.SuggestBooks = channel.unary_unary(
                '/suggestions.SuggestionService/SuggestBooks',
                request_serializer=utils_dot_utils__pb2.ContinuationRequest.SerializeToString,
                response_deserializer=suggestions_dot_suggestions__pb2.SuggestionResponse.FromString,
                )
        self.ClearOrder = channel.unary_unary(
                '/suggestions.SuggestionService/ClearOrder',
                request_serializer=utils_dot_utils__pb2.ContinuationRequest.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )


class SuggestionServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def InitOrder(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SuggestBooks(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ClearOrder(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_SuggestionServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'InitOrder': grpc.unary_unary_rpc_method_handler(
                    servicer.InitOrder,
                    request_deserializer=suggestions_dot_suggestions__pb2.InitializationRequest.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'SuggestBooks': grpc.unary_unary_rpc_method_handler(
                    servicer.SuggestBooks,
                    request_deserializer=utils_dot_utils__pb2.ContinuationRequest.FromString,
                    response_serializer=suggestions_dot_suggestions__pb2.SuggestionResponse.SerializeToString,
            ),
            'ClearOrder': grpc.unary_unary_rpc_method_handler(
                    servicer.ClearOrder,
                    request_deserializer=utils_dot_utils__pb2.ContinuationRequest.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'suggestions.SuggestionService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class SuggestionService(object):
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
        return grpc.experimental.unary_unary(request, target, '/suggestions.SuggestionService/InitOrder',
            suggestions_dot_suggestions__pb2.InitializationRequest.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SuggestBooks(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/suggestions.SuggestionService/SuggestBooks',
            utils_dot_utils__pb2.ContinuationRequest.SerializeToString,
            suggestions_dot_suggestions__pb2.SuggestionResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ClearOrder(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/suggestions.SuggestionService/ClearOrder',
            utils_dot_utils__pb2.ContinuationRequest.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
