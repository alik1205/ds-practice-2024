# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: order_executor.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14order_executor.proto\x12\x0eorder_executor\"$\n\x16\x45lectionMessageRequest\x12\n\n\x02id\x18\x01 \x01(\t\"*\n\x17\x45lectionMessageResponse\x12\x0f\n\x07message\x18\x01 \x01(\t\"\x15\n\x13\x44\x65queueOrderRequest\"9\n\x14\x44\x65queueOrderResponse\x12\x0f\n\x07orderId\x18\x01 \x01(\t\x12\x10\n\x08\x64\x65queued\x18\x02 \x01(\x08\x32\xc3\x02\n\rOrderExecutor\x12h\n\x13SendElectionMessage\x12&.order_executor.ElectionMessageRequest\x1a\'.order_executor.ElectionMessageResponse\"\x00\x12k\n\x16ReceiveElectionMessage\x12&.order_executor.ElectionMessageRequest\x1a\'.order_executor.ElectionMessageResponse\"\x00\x12[\n\x0c\x44\x65queueOrder\x12#.order_executor.DequeueOrderRequest\x1a$.order_executor.DequeueOrderResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'order_executor_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_ELECTIONMESSAGEREQUEST']._serialized_start=40
  _globals['_ELECTIONMESSAGEREQUEST']._serialized_end=76
  _globals['_ELECTIONMESSAGERESPONSE']._serialized_start=78
  _globals['_ELECTIONMESSAGERESPONSE']._serialized_end=120
  _globals['_DEQUEUEORDERREQUEST']._serialized_start=122
  _globals['_DEQUEUEORDERREQUEST']._serialized_end=143
  _globals['_DEQUEUEORDERRESPONSE']._serialized_start=145
  _globals['_DEQUEUEORDERRESPONSE']._serialized_end=202
  _globals['_ORDEREXECUTOR']._serialized_start=205
  _globals['_ORDEREXECUTOR']._serialized_end=528
# @@protoc_insertion_point(module_scope)