import abc, enum, typing

_Ta = typing.TypeVar("_Ta")
_Ps = typing.ParamSpec("_Ps")

RawMapping = typing.Mapping[str, str]
StringMappedAlias = MappedAlias[typing.LiteralString]
IntMappedAlias = MappedAlias[int]
Unknown = UnknownType()
Validator = typing.Callable[typing.Concatenate[ModelI, _Ps], bool]
"""
Callable returning whether object passes
validation.
"""

def isvalidator(callable: typing.Callable) -> bool:
    """
    Whether the given callable is a `Validator`.
    """
@typing.overload
def validator(**params) -> Validator: ...
@typing.overload
def validator(callable: Validator, /) -> Validator:
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
    def __get__(self, owner: object, owner_cls: type = ...) -> _Ta: ...
    def __init__(self, alias: str, default: typing.Optional[_Ta] = ...) -> None: ...
    def __set__(self, owner: object, value: _Ta): ...
    def __set_name__(self, owner: object): ...

class ModelI(typing.Protocol):
    """
    XNAT Object from RESTful representation.
    """

    __validators__: typing.Iterable[Validator]

    @property
    def is_valid(self) -> bool:
        """
        Whether this object is a valid instance.
        """
    @property
    def label(self) -> typing.LiteralString:
        """Serial label of this object."""
    @property
    def name(self) -> typing.LiteralString | None:
        """Human readable label of this object."""
    @classmethod
    def from_mapping(cls, model_cls: type[typing.Self], mapping: RawMapping) -> typing.Self:
        """
        Transform a mapping into the given model
        class.
        """
    @classmethod
    def into_mapping(cls, model: typing.Self) -> RawMapping:
        """
        Transform a model instance into a mapping
        of it's values.
        """
    @classmethod
    def insert_validator(cls, callable: Validator) -> None:
        """
        Insert a validator into this model's
        validators.
        """
    @classmethod
    def remove_validator(cls, callable: Validator) -> Validator:
        """
        Remove the validator from this model's validators.
        """
    @classmethod
    def __from_mapping__(cls, mapping: RawMapping) -> typing.Self: ...
    def __into_mapping__(self) -> RawMapping: ...
    def __validate__(self) -> bool: ...
    def __init__(self, **kwds) -> None: ...
    def __repr__(self) -> typing.LiteralString: ...
    def __str__(self) -> typing.LiteralString: ...

class ModelMeta(abc.ABCMeta): ...

@typing.dataclass_transform()
class Model(ModelI, metaclass=ModelMeta):
    URI: typing.LiteralString

class File(Model, metaclass=ModelMeta):
    """File in XNAT archive."""
    cat_id: typing.Annotated[StringMappedAlias, "cat_ID", Unknown]
    content: typing.Annotated[StringMappedAlias, "file_content", Unknown]
    format: typing.Annotated[StringMappedAlias, "file_format", Unknown]
    name: typing.LiteralString
    size: typing.Annotated[IntMappedAlias, "Size", 0]
    tags: typing.Annotated[MappedAlias[tuple[str]], "file_tags", ()]

class Image(File, metaclass=ModelMeta):
    """
    Individual image file and it's metadata.
    """

class Project(Model, metaclass=ModelMeta):
    """
    Top-level or *root* object in XNAT archive
    heirarchy.
    """

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
    data_type: typing.Annotated[StringMappedAlias, "type", Unknown]
    description: typing.LiteralString
    id: typing.Annotated[IntMappedAlias, "ID", 0]
    project: Project
    quality: typing.Annotated[MappedAlias[ScanQuality], "quality"]
    session: Session
    xsi_type: typing.Annotated[StringMappedAlias, "xsiType", Unknown]

class ScanQuality(enum.StrEnum):
    """Quality of the scan."""

class Session(Model, metaclass=ModelMeta):
    """
    A series or collection of related `Scan`
    objects.
    """
    id: typing.Annotated[IntMappedAlias, "xnat:subjectassessordata/id", Unknown]
    project: Project
    subject_label: typing.Annotated[StringMappedAlias, "subject_label", Unknown]
    xsi_type: typing.Annotated[StringMappedAlias, "xsiType", ""]

@typing.final
class UnknownType: ...

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
