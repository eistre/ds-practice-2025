from google.protobuf import empty_pb2 as _empty_pb2
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
    user: User
    credit_card: CreditCard
    def __init__(self, order_id: _Optional[str] = ..., user: _Optional[_Union[User, _Mapping]] = ..., credit_card: _Optional[_Union[CreditCard, _Mapping]] = ...) -> None: ...

class ContinuationRequest(_message.Message):
    __slots__ = ("order_id",)
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    order_id: str
    def __init__(self, order_id: _Optional[str] = ...) -> None: ...

class DetectionResponse(_message.Message):
    __slots__ = ("is_fraud",)
    IS_FRAUD_FIELD_NUMBER: _ClassVar[int]
    is_fraud: bool
    def __init__(self, is_fraud: bool = ...) -> None: ...

class User(_message.Message):
    __slots__ = ("name", "contact", "address")
    NAME_FIELD_NUMBER: _ClassVar[int]
    CONTACT_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    name: str
    contact: str
    address: Address
    def __init__(self, name: _Optional[str] = ..., contact: _Optional[str] = ..., address: _Optional[_Union[Address, _Mapping]] = ...) -> None: ...

class Address(_message.Message):
    __slots__ = ("street", "city", "state", "zip", "country")
    STREET_FIELD_NUMBER: _ClassVar[int]
    CITY_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    ZIP_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    street: str
    city: str
    state: str
    zip: str
    country: str
    def __init__(self, street: _Optional[str] = ..., city: _Optional[str] = ..., state: _Optional[str] = ..., zip: _Optional[str] = ..., country: _Optional[str] = ...) -> None: ...

class CreditCard(_message.Message):
    __slots__ = ("number", "expiration_date", "cvv")
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    EXPIRATION_DATE_FIELD_NUMBER: _ClassVar[int]
    CVV_FIELD_NUMBER: _ClassVar[int]
    number: str
    expiration_date: str
    cvv: str
    def __init__(self, number: _Optional[str] = ..., expiration_date: _Optional[str] = ..., cvv: _Optional[str] = ...) -> None: ...
