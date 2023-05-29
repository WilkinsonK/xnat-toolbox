__all__ =\
(
    "ModelI",
    "ModelMeta"
)

import abc, typing


class ModelI(typing.Protocol):
    pass


class ModelMeta(abc.ABCMeta):
    pass
