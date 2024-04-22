from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class EnqueueRequest(_message.Message):
    __slots__ = ("orderId",)
    ORDERID_FIELD_NUMBER: _ClassVar[int]
    orderId: str
    def __init__(self, orderId: _Optional[str] = ...) -> None: ...

class EnqueueResponse(_message.Message):
    __slots__ = ("orderId", "Enqueued")
    ORDERID_FIELD_NUMBER: _ClassVar[int]
    ENQUEUED_FIELD_NUMBER: _ClassVar[int]
    orderId: str
    Enqueued: bool
    def __init__(self, orderId: _Optional[str] = ..., Enqueued: bool = ...) -> None: ...

class DequeueRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class DequeueResponse(_message.Message):
    __slots__ = ("orderId", "Dequeued")
    ORDERID_FIELD_NUMBER: _ClassVar[int]
    DEQUEUED_FIELD_NUMBER: _ClassVar[int]
    orderId: str
    Dequeued: bool
    def __init__(self, orderId: _Optional[str] = ..., Dequeued: bool = ...) -> None: ...
