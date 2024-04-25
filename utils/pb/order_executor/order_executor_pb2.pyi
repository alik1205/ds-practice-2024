from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ElectionMessageRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ElectionMessageResponse(_message.Message):
    __slots__ = ("message",)
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    message: str
    def __init__(self, message: _Optional[str] = ...) -> None: ...

class DequeueOrderRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DequeueOrderResponse(_message.Message):
    __slots__ = ("orderId", "dequeued")
    ORDERID_FIELD_NUMBER: _ClassVar[int]
    DEQUEUED_FIELD_NUMBER: _ClassVar[int]
    orderId: str
    dequeued: bool
    def __init__(self, orderId: _Optional[str] = ..., dequeued: bool = ...) -> None: ...
