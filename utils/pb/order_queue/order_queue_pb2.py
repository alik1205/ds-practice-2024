# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: order_queue.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11order_queue.proto\x12\x0border_queue\"!\n\x0e\x45nqueueRequest\x12\x0f\n\x07orderId\x18\x01 \x01(\t\"4\n\x0f\x45nqueueResponse\x12\x0f\n\x07orderId\x18\x01 \x01(\t\x12\x10\n\x08\x45nqueued\x18\x02 \x01(\x08\"\x10\n\x0e\x44\x65queueRequest\"4\n\x0f\x44\x65queueResponse\x12\x0f\n\x07orderId\x18\x01 \x01(\t\x12\x10\n\x08\x44\x65queued\x18\x02 \x01(\x08\x32\xa2\x01\n\nOrderQueue\x12I\n\x0c\x45nqueueOrder\x12\x1b.order_queue.EnqueueRequest\x1a\x1c.order_queue.EnqueueResponse\x12I\n\x0c\x44\x65queueOrder\x12\x1b.order_queue.DequeueRequest\x1a\x1c.order_queue.DequeueResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'order_queue_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_ENQUEUEREQUEST']._serialized_start=34
  _globals['_ENQUEUEREQUEST']._serialized_end=67
  _globals['_ENQUEUERESPONSE']._serialized_start=69
  _globals['_ENQUEUERESPONSE']._serialized_end=121
  _globals['_DEQUEUEREQUEST']._serialized_start=123
  _globals['_DEQUEUEREQUEST']._serialized_end=139
  _globals['_DEQUEUERESPONSE']._serialized_start=141
  _globals['_DEQUEUERESPONSE']._serialized_end=193
  _globals['_ORDERQUEUE']._serialized_start=196
  _globals['_ORDERQUEUE']._serialized_end=358
# @@protoc_insertion_point(module_scope)
