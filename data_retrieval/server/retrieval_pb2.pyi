from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class RetrievalAggregates(_message.Message):
    __slots__ = ["name", "partition", "predicted_value", "range", "typology", "value"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PARTITION_FIELD_NUMBER: _ClassVar[int]
    PREDICTED_VALUE_FIELD_NUMBER: _ClassVar[int]
    RANGE_FIELD_NUMBER: _ClassVar[int]
    TYPOLOGY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    name: str
    partition: str
    predicted_value: float
    range: str
    typology: str
    value: float
    def __init__(self, name: _Optional[str] = ..., partition: _Optional[str] = ..., range: _Optional[str] = ..., typology: _Optional[str] = ..., value: _Optional[float] = ..., predicted_value: _Optional[float] = ...) -> None: ...

class RetrievalAutocorrelation(_message.Message):
    __slots__ = ["name", "partition", "value"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PARTITION_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    name: str
    partition: str
    value: float
    def __init__(self, name: _Optional[str] = ..., partition: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...

class RetrievalDecomposition(_message.Message):
    __slots__ = ["name", "partition", "timestamp", "typology", "value"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PARTITION_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    TYPOLOGY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    name: str
    partition: str
    timestamp: str
    typology: str
    value: float
    def __init__(self, name: _Optional[str] = ..., partition: _Optional[str] = ..., timestamp: _Optional[str] = ..., typology: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...

class RetrievalDickeyFuller(_message.Message):
    __slots__ = ["crit_value1", "crit_value10", "crit_value5", "is_stationary", "name", "p_value", "partition", "test_statistic"]
    CRIT_VALUE10_FIELD_NUMBER: _ClassVar[int]
    CRIT_VALUE1_FIELD_NUMBER: _ClassVar[int]
    CRIT_VALUE5_FIELD_NUMBER: _ClassVar[int]
    IS_STATIONARY_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PARTITION_FIELD_NUMBER: _ClassVar[int]
    P_VALUE_FIELD_NUMBER: _ClassVar[int]
    TEST_STATISTIC_FIELD_NUMBER: _ClassVar[int]
    crit_value1: float
    crit_value10: float
    crit_value5: float
    is_stationary: bool
    name: str
    p_value: float
    partition: str
    test_statistic: float
    def __init__(self, name: _Optional[str] = ..., partition: _Optional[str] = ..., test_statistic: _Optional[float] = ..., p_value: _Optional[float] = ..., is_stationary: bool = ..., crit_value1: _Optional[float] = ..., crit_value5: _Optional[float] = ..., crit_value10: _Optional[float] = ...) -> None: ...

class RetrievalHodrickPrescott(_message.Message):
    __slots__ = ["name", "partition", "timestamp", "value"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PARTITION_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    name: str
    partition: str
    timestamp: str
    value: float
    def __init__(self, name: _Optional[str] = ..., partition: _Optional[str] = ..., timestamp: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...

class RetrievalRequest(_message.Message):
    __slots__ = ["query"]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    query: str
    def __init__(self, query: _Optional[str] = ...) -> None: ...
