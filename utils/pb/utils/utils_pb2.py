# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: utils/utils.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11utils/utils.proto\x12\x05utils\"Q\n\x13\x43ontinuationRequest\x12\x10\n\x08order_id\x18\x01 \x01(\t\x12(\n\x0cvector_clock\x18\x02 \x01(\x0b\x32\x12.utils.VectorClock\"F\n\x04User\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07\x63ontact\x18\x02 \x01(\t\x12\x1f\n\x07\x61\x64\x64ress\x18\x03 \x01(\x0b\x32\x0e.utils.Address\"T\n\x07\x41\x64\x64ress\x12\x0e\n\x06street\x18\x01 \x01(\t\x12\x0c\n\x04\x63ity\x18\x02 \x01(\t\x12\r\n\x05state\x18\x03 \x01(\t\x12\x0b\n\x03zip\x18\x04 \x01(\t\x12\x0f\n\x07\x63ountry\x18\x05 \x01(\t\"B\n\nCreditCard\x12\x0e\n\x06number\x18\x01 \x01(\t\x12\x17\n\x0f\x65xpiration_date\x18\x02 \x01(\t\x12\x0b\n\x03\x63vv\x18\x03 \x01(\t\"&\n\x04Item\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x10\n\x08quantity\x18\x02 \x01(\x05\"\x1c\n\x0bVectorClock\x12\r\n\x05\x63lock\x18\x01 \x03(\x05\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'utils.utils_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_CONTINUATIONREQUEST']._serialized_start=28
  _globals['_CONTINUATIONREQUEST']._serialized_end=109
  _globals['_USER']._serialized_start=111
  _globals['_USER']._serialized_end=181
  _globals['_ADDRESS']._serialized_start=183
  _globals['_ADDRESS']._serialized_end=267
  _globals['_CREDITCARD']._serialized_start=269
  _globals['_CREDITCARD']._serialized_end=335
  _globals['_ITEM']._serialized_start=337
  _globals['_ITEM']._serialized_end=375
  _globals['_VECTORCLOCK']._serialized_start=377
  _globals['_VECTORCLOCK']._serialized_end=405
# @@protoc_insertion_point(module_scope)
