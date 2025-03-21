# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: fraud_detection.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15\x66raud_detection.proto\x12\x0f\x66raud_detection\x1a\x1bgoogle/protobuf/empty.proto\"\x80\x01\n\x15InitializationRequest\x12\x10\n\x08order_id\x18\x01 \x01(\t\x12#\n\x04user\x18\x02 \x01(\x0b\x32\x15.fraud_detection.User\x12\x30\n\x0b\x63redit_card\x18\x03 \x01(\x0b\x32\x1b.fraud_detection.CreditCard\"\'\n\x13\x43ontinuationRequest\x12\x10\n\x08order_id\x18\x01 \x01(\t\"%\n\x11\x44\x65tectionResponse\x12\x10\n\x08is_fraud\x18\x01 \x01(\x08\"P\n\x04User\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07\x63ontact\x18\x02 \x01(\t\x12)\n\x07\x61\x64\x64ress\x18\x03 \x01(\x0b\x32\x18.fraud_detection.Address\"T\n\x07\x41\x64\x64ress\x12\x0e\n\x06street\x18\x01 \x01(\t\x12\x0c\n\x04\x63ity\x18\x02 \x01(\t\x12\r\n\x05state\x18\x03 \x01(\t\x12\x0b\n\x03zip\x18\x04 \x01(\t\x12\x0f\n\x07\x63ountry\x18\x05 \x01(\t\"B\n\nCreditCard\x12\x0e\n\x06number\x18\x01 \x01(\t\x12\x17\n\x0f\x65xpiration_date\x18\x02 \x01(\t\x12\x0b\n\x03\x63vv\x18\x03 \x01(\t2\xa2\x02\n\x15\x46raudDetectionService\x12M\n\tInitOrder\x12&.fraud_detection.InitializationRequest\x1a\x16.google.protobuf.Empty\"\x00\x12[\n\rCheckUserData\x12$.fraud_detection.ContinuationRequest\x1a\".fraud_detection.DetectionResponse\"\x00\x12]\n\x0f\x43heckCreditCard\x12$.fraud_detection.ContinuationRequest\x1a\".fraud_detection.DetectionResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'fraud_detection_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_INITIALIZATIONREQUEST']._serialized_start=72
  _globals['_INITIALIZATIONREQUEST']._serialized_end=200
  _globals['_CONTINUATIONREQUEST']._serialized_start=202
  _globals['_CONTINUATIONREQUEST']._serialized_end=241
  _globals['_DETECTIONRESPONSE']._serialized_start=243
  _globals['_DETECTIONRESPONSE']._serialized_end=280
  _globals['_USER']._serialized_start=282
  _globals['_USER']._serialized_end=362
  _globals['_ADDRESS']._serialized_start=364
  _globals['_ADDRESS']._serialized_end=448
  _globals['_CREDITCARD']._serialized_start=450
  _globals['_CREDITCARD']._serialized_end=516
  _globals['_FRAUDDETECTIONSERVICE']._serialized_start=519
  _globals['_FRAUDDETECTIONSERVICE']._serialized_end=809
# @@protoc_insertion_point(module_scope)
