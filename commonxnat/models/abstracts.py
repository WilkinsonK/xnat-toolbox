import abc, typing

_Ta = typing.TypeVar("_Ta")


class MappedAlias(typing.Generic[_Ta]):

    @property
    def alias(self):
        return self._alias
    
    @property
    def default(self):
        return self._default

    def __get__(self, owner, owner_cls=None) -> _Ta:
        return getattr(owner, self.private_name)

    def __set__(self, owner, value):
        setattr(owner, self.private_name, value)

    def __set_name__(self, owner, name):
        self.private_name = f"__{owner.__qualname__}_{name}_"

    def __init__(self, alias, default=None):
        self._alias = alias
        self._default = default


@typing.dataclass_transform(field_specifiers=(MappedAlias,))
class ModelMeta(typing._ProtocolMeta, abc.ABCMeta):
    pass


class ModelI(typing.Protocol, metaclass=ModelMeta):
    pass


@typing.final
class UnknownType(int):
    """Some unknown value."""

    def __new__(cls):
        return super().__new__(cls, 0)


_Ps = typing.ParamSpec("_Ps")

Unknown = UnknownType()
Validator = typing.Callable[typing.Concatenate[ModelI, _Ps], bool]
