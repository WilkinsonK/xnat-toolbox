import dataclasses, functools, typing, warnings

from models.abstracts import MappedAlias, ModelI, ModelMeta, Unknown, Validator
from models.errors import ValidatorExists, NotAValidator

_IS_VALIDATOR_ATTR = "__is_validator__"
_model_dataclass = dataclasses.dataclass()


def isvalidator(fn):
    return (callable(fn) and getattr(fn, _IS_VALIDATOR_ATTR, False))


def validator(fn=None, *, model=None, **kwds):

    def inner(wrapped: Validator):
        wrapper = functools.wraps(wrapped)
        wrapped = wrapper(functools.partial(wrapped, **kwds))
        setattr(wrapped, _IS_VALIDATOR_ATTR, True)

        if model:
            model.insert_validator(wrapped)
        return wrapped

    if fn:
        return inner(fn)
    else:
        return inner


def _warn_validator_exists(cls, fn):
    warnings.warn(f"{cls!s} already has the validator {fn!r} registered.")


@_model_dataclass
class Model(ModelI, metaclass=ModelMeta):
    URI: typing.LiteralString

    @functools.cached_property
    def is_valid(self):
        return self.__validate__()

    @classmethod
    def from_mapping(cls, model_cls, mapping):
        return model_cls.__from_mapping__(mapping)

    @classmethod
    def into_mapping(cls, model):
        return model.__into_mapping__()

    @classmethod
    def insert_validator(cls, fn):
        if fn in cls.__validators__:
            raise ValidatorExists(f"Validator {fn!r} already registered.")
        if not isvalidator(fn):
            raise NotAValidator(f"{fn!r} is not a validator callable.")
        cls.__validators__.add(fn)

    @classmethod
    def remove_validator(cls, fn):
        if fn not in cls.__validators__:
            raise NotAValidator(f"Validator {fn!r} does not exist.")
        cls.__validators__.remove(fn)

    @classmethod
    def __from_mapping__(cls, mapping):
        for name, alias in cls.__mapped_aliases__.items():
            if not alias.alias in mapping:
                continue
            mapping[name] = mapping.pop(alias.alias, alias.default)

        return cls(**mapping)

    def __into_mapping__(self):
        mapping = dataclasses.asdict(self)

        for name in tuple(mapping.keys()): # Make copy of keys.
            alias = self.__mapped_aliases__.get(name, None)
            if not alias:
                continue
            mapping[alias.alias] = mapping.pop(name, alias.default)

        return mapping

    def __validate__(self):
        return all([fn(self) for fn in self.__validators__])

    def __init_subclass__(cls):
        cls.__validators__ = set()
        cls.__mapped_aliases__ = dict()

        for name in dir(cls):
            attr = getattr(cls, name, None)
            if not (attr and isvalidator(attr)):
                continue

            try:
                cls.insert_validator(attr)
            except ValueError: # Validator already exists.
                _warn_validator_exists(cls, attr)

        # Parse out dynamic aliasing of model values.
        rhints = typing.get_type_hints(cls, include_extras=False)
        ehints = typing.get_type_hints(cls, include_extras=True)
        for name in rhints:
            origin = typing.get_origin(ehints[name])
            if origin not in (typing.Annotated, MappedAlias):
                continue

            if origin == typing.Annotated:
                origin = typing.get_origin(rhints[name])

            if origin != MappedAlias:
                continue

            args = typing.get_args(origin)
            if not args:
                args = typing.get_args(ehints[name])[1:]
            if not args:
                continue # Second pass. If not annotated it's just a type hint.

            setattr(cls, name, origin(*args))

        for name, origin in cls.__dict__.items():
            if isinstance(origin, MappedAlias):
                cls.__mapped_aliases__[name] = origin

    def __repr__(self):
        return f"<{self.__class__.__qualname__}({self.label}) @ {hex(id(self))}>"


@_model_dataclass
class Session(Model):
    id: MappedAlias[int] = MappedAlias[int]("xnat:subjectassessordata/id", Unknown)
