from google.protobuf import empty_pb2 as _empty_pb2
from utils import utils_pb2 as _utils_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class InitializationRequest(_message.Message):
    __slots__ = ("order_id", "user", "items", "credit_card")
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    CREDIT_CARD_FIELD_NUMBER: _ClassVar[int]
    order_id: str
    user: _utils_pb2.User
    items: _containers.RepeatedCompositeFieldContainer[_utils_pb2.Item]
    credit_card: _utils_pb2.CreditCard
    def __init__(self, order_id: _Optional[str] = ..., user: _Optional[_Union[_utils_pb2.User, _Mapping]] = ..., items: _Optional[_Iterable[_Union[_utils_pb2.Item, _Mapping]]] = ..., credit_card: _Optional[_Union[_utils_pb2.CreditCard, _Mapping]] = ...) -> None: ...

class VerificationResponse(_message.Message):
    __slots__ = ("verified",)
    VERIFIED_FIELD_NUMBER: _ClassVar[int]
    verified: bool
    def __init__(self, verified: bool = ...) -> None: ...
