from google.protobuf import empty_pb2 as _empty_pb2
from utils import utils_pb2 as _utils_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class InitializationRequest(_message.Message):
    __slots__ = ("order_id", "items", "vector_clock")
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    VECTOR_CLOCK_FIELD_NUMBER: _ClassVar[int]
    order_id: str
    items: _containers.RepeatedCompositeFieldContainer[_utils_pb2.Item]
    vector_clock: _utils_pb2.VectorClock
    def __init__(self, order_id: _Optional[str] = ..., items: _Optional[_Iterable[_Union[_utils_pb2.Item, _Mapping]]] = ..., vector_clock: _Optional[_Union[_utils_pb2.VectorClock, _Mapping]] = ...) -> None: ...

class SuggestionResponse(_message.Message):
    __slots__ = ("books", "vector_clock")
    BOOKS_FIELD_NUMBER: _ClassVar[int]
    VECTOR_CLOCK_FIELD_NUMBER: _ClassVar[int]
    books: _containers.RepeatedCompositeFieldContainer[Book]
    vector_clock: _utils_pb2.VectorClock
    def __init__(self, books: _Optional[_Iterable[_Union[Book, _Mapping]]] = ..., vector_clock: _Optional[_Union[_utils_pb2.VectorClock, _Mapping]] = ...) -> None: ...

class Book(_message.Message):
    __slots__ = ("book_id", "title", "author")
    BOOK_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    book_id: str
    title: str
    author: str
    def __init__(self, book_id: _Optional[str] = ..., title: _Optional[str] = ..., author: _Optional[str] = ...) -> None: ...
