# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: suggestions/suggestions.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from utils import utils_pb2 as utils_dot_utils__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1dsuggestions/suggestions.proto\x12\x0bsuggestions\x1a\x1bgoogle/protobuf/empty.proto\x1a\x11utils/utils.proto\"E\n\x15InitializationRequest\x12\x10\n\x08order_id\x18\x01 \x01(\t\x12\x1a\n\x05items\x18\x02 \x03(\x0b\x32\x0b.utils.Item\"6\n\x12SuggestionResponse\x12 \n\x05\x62ooks\x18\x01 \x03(\x0b\x32\x11.suggestions.Book\"6\n\x04\x42ook\x12\x0f\n\x07\x62ook_id\x18\x01 \x01(\t\x12\r\n\x05title\x18\x02 \x01(\t\x12\x0e\n\x06\x61uthor\x18\x03 \x01(\t2\xf1\x01\n\x11SuggestionService\x12I\n\tInitOrder\x12\".suggestions.InitializationRequest\x1a\x16.google.protobuf.Empty\"\x00\x12M\n\x0cSuggestBooks\x12\x1a.utils.ContinuationRequest\x1a\x1f.suggestions.SuggestionResponse\"\x00\x12\x42\n\nClearOrder\x12\x1a.utils.ContinuationRequest\x1a\x16.google.protobuf.Empty\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'suggestions.suggestions_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_INITIALIZATIONREQUEST']._serialized_start=94
  _globals['_INITIALIZATIONREQUEST']._serialized_end=163
  _globals['_SUGGESTIONRESPONSE']._serialized_start=165
  _globals['_SUGGESTIONRESPONSE']._serialized_end=219
  _globals['_BOOK']._serialized_start=221
  _globals['_BOOK']._serialized_end=275
  _globals['_SUGGESTIONSERVICE']._serialized_start=278
  _globals['_SUGGESTIONSERVICE']._serialized_end=519
# @@protoc_insertion_point(module_scope)
