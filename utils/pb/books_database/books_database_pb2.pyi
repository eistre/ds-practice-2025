from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ReadRequest(_message.Message):
    __slots__ = ("title",)
    TITLE_FIELD_NUMBER: _ClassVar[int]
    title: str
    def __init__(self, title: _Optional[str] = ...) -> None: ...

class ReadResponse(_message.Message):
    __slots__ = ("stock",)
    STOCK_FIELD_NUMBER: _ClassVar[int]
    stock: int
    def __init__(self, stock: _Optional[int] = ...) -> None: ...

class WriteRequest(_message.Message):
    __slots__ = ("title", "quantity")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    title: str
    quantity: int
    def __init__(self, title: _Optional[str] = ..., quantity: _Optional[int] = ...) -> None: ...

class WriteResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class TransactionRequest(_message.Message):
    __slots__ = ("order_id", "updates")
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    UPDATES_FIELD_NUMBER: _ClassVar[int]
    order_id: str
    updates: _containers.RepeatedCompositeFieldContainer[WriteRequest]
    def __init__(self, order_id: _Optional[str] = ..., updates: _Optional[_Iterable[_Union[WriteRequest, _Mapping]]] = ...) -> None: ...

class PrepareResponse(_message.Message):
    __slots__ = ("ready",)
    READY_FIELD_NUMBER: _ClassVar[int]
    ready: bool
    def __init__(self, ready: bool = ...) -> None: ...

class CommitResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class AbortResponse(_message.Message):
    __slots__ = ("aborted",)
    ABORTED_FIELD_NUMBER: _ClassVar[int]
    aborted: bool
    def __init__(self, aborted: bool = ...) -> None: ...
