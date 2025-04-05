from google.protobuf import empty_pb2 as _empty_pb2
from utils import utils_pb2 as _utils_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EnqueueRequest(_message.Message):
    __slots__ = ("order_id", "user", "items")
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    order_id: str
    user: _utils_pb2.User
    items: _containers.RepeatedCompositeFieldContainer[_utils_pb2.Item]
    def __init__(self, order_id: _Optional[str] = ..., user: _Optional[_Union[_utils_pb2.User, _Mapping]] = ..., items: _Optional[_Iterable[_Union[_utils_pb2.Item, _Mapping]]] = ...) -> None: ...

class EnqueueResponse(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...

class DequeueResponse(_message.Message):
    __slots__ = ("order_id",)
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    order_id: str
    def __init__(self, order_id: _Optional[str] = ...) -> None: ...
