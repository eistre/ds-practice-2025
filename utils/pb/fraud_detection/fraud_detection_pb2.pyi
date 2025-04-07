from google.protobuf import empty_pb2 as _empty_pb2
from utils import utils_pb2 as _utils_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class InitializationRequest(_message.Message):
    __slots__ = ("order_id", "user", "credit_card")
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    CREDIT_CARD_FIELD_NUMBER: _ClassVar[int]
    order_id: str
    user: _utils_pb2.User
    credit_card: _utils_pb2.CreditCard
    def __init__(self, order_id: _Optional[str] = ..., user: _Optional[_Union[_utils_pb2.User, _Mapping]] = ..., credit_card: _Optional[_Union[_utils_pb2.CreditCard, _Mapping]] = ...) -> None: ...

class DetectionResponse(_message.Message):
    __slots__ = ("is_fraud", "vector_clock")
    IS_FRAUD_FIELD_NUMBER: _ClassVar[int]
    VECTOR_CLOCK_FIELD_NUMBER: _ClassVar[int]
    is_fraud: bool
    vector_clock: _utils_pb2.VectorClock
    def __init__(self, is_fraud: bool = ..., vector_clock: _Optional[_Union[_utils_pb2.VectorClock, _Mapping]] = ...) -> None: ...
