import abc, dataclasses, enum, typing

_Ta = typing.TypeVar("_Ta")
_Ps = typing.ParamSpec("_Ps")

RawMapping = typing.Mapping[str, str]
StringMappedAlias = MappedAlias[typing.LiteralString]
IntMappedAlias = MappedAlias[int]
Unknown = Ellipsis
Validator = typing.Callable[typing.Concatenate[ModelI, _Ps], bool]
"""
Callable returning whether object passes
validation.
"""

def isvalidator(fn: typing.Callable) -> bool:
    """
    Whether the given callable is a `Validator`.
    """
@typing.overload
def validator(**params) -> Validator: ...
@typing.overload
def validator(fn: Validator, /) -> Validator:
    """
    Marks some callable as a validator function.
    """

class MappedAlias(typing.Generic[_Ta]):
    """
    Mapped alias to attribute name. When a model
    is translated into or from a mapping, this
    alias is used bridge the gap from the `Model`
    object to the REST response from XNAT.
    """

    @property
    def alias(self) -> typing.LiteralString: ...
    @property
    def default(self) -> _Ta | None: ...
    @property
    def factory(self) -> typing.Callable[[typing.Any], _Ta]: ...
    def __get__(self, owner: object, owner_cls: type | None) -> _Ta: ...
    def __init__(self, alias: str, factory: typing.Optional[typing.Callable[[typing.Any], _Ta]] = ..., default: typing.Optional[_Ta] = ...) -> None: ...
    def __set__(self, owner: object, value: _Ta) -> None: ...
    def __set_name__(self, owner: object, name: str): ...

class ModelI(typing.Protocol):
    """
    XNAT Object from RESTful representation.
    """

    __mapped_aliases__: typing.ClassVar[dict[str, MappedAlias]]
    __validators__: typing.ClassVar[typing.Iterable[Validator]]

    @property
    def is_valid(self) -> bool:
        """
        Whether this object is a valid instance.
        """
    @property
    def name(self) -> typing.LiteralString | None:
        """Human readable label of this object."""
    @classmethod
    def from_mapping(cls, model_cls: type[typing.Self], mapping: RawMapping) -> typing.Self:
        """
        Transform a mapping into the given model
        class.
        """
    @typing.overload
    @classmethod
    def into_mapping(cls) -> RawMapping: ...
    @typing.overload
    @classmethod
    def into_mapping(cls, model: typing.Self) -> RawMapping:
        """
        Transform a model instance into a mapping
        of it's values.
        """
    @classmethod
    def insert_validator(cls, fn: Validator) -> None:
        """
        Insert a validator into this model's
        validators.
        """
    @classmethod
    def remove_validator(cls, fn: Validator) -> None:
        """
        Remove the validator from this model's validators.
        """
    @classmethod
    def __from_mapping__(cls, mapping: RawMapping) -> typing.Self: ...
    def __into_mapping__(self) -> RawMapping: ...
    def __validate__(self) -> bool: ...
    def __init__(self, **kwds) -> None: ...
    def __init_subclass__(cls) -> None: ...
    def __repr__(self) -> typing.LiteralString: ...

@typing.dataclass_transform()
class ModelMeta(abc.ABCMeta): ...

class Model(ModelI, metaclass=ModelMeta):
    _: dataclasses.KW_ONLY
    file_uri: typing.LiteralString
    rest_uri: MappedAlias[typing.LiteralString]

class File(Model, metaclass=ModelMeta):
    """File in XNAT archive."""
    cat_id: StringMappedAlias
    name: typing.LiteralString
    _: dataclasses.KW_ONLY
    content: StringMappedAlias
    format: StringMappedAlias
    size: IntMappedAlias
    tags: MappedAlias[tuple[str]]

class Image(File, metaclass=ModelMeta):
    """
    Individual image file and it's metadata.
    """

class Project(Model, metaclass=ModelMeta):
    """
    Top-level or *root* object in XNAT archive
    heirarchy.
    """
    project_label: str

class Resource(Model, metaclass=ModelMeta):
    """
    Additional `File` data related to the parent
    object.
    """

class Scan(Model, metaclass=ModelMeta):
    """
    Individual scan object pertaining to one or
    more individual `Image`(s).
    """
    description: typing.LiteralString
    id: IntMappedAlias
    quality: MappedAlias[ScanQuality]
    session: Session
    _: dataclasses.KW_ONLY
    data_type: StringMappedAlias
    xsi_type: StringMappedAlias

class ScanQuality(enum.StrEnum):
    """Quality of the scan."""

class Session(Model, metaclass=ModelMeta):
    """
    A series or collection of related `Scan`
    objects.
    """
    id: IntMappedAlias
    project: Project
    session_label: str
    _: dataclasses.KW_ONLY
    subject_label: StringMappedAlias
    xsi_type: StringMappedAlias


class ModelError(Exception):
    """
    Raised for unexpected/unintended behaviors
    related to XNAT Models.
    """

class ValidatorExists(ModelError):
    """
    Raised when a validator already exists in the
    model's validators.
    """

class NotAValidator(ModelError):
    """
    Raised when an object does not qualify as a
    Validator.
    """
