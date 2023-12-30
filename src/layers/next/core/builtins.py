"""
Built-in types of BS
"""
from __future__ import annotations
import binascii
from typing import Any, Generic, TypeVar
# from typing import override

class BSMeta:
    """
    Metaclass for BinaryScheme protocol.
    Please make sure that there is only BSMeta in your program.
    BSMeta is used for preventing collisions in constructor names and
    the scheme will be totally broken if there is more then one BSMeta instance.
    
    Please import `BS` instead of `BSMeta`.
    """
    def __init__(self) -> None:
        self.used_constructors: dict[str, BSType] = {} # constructor_name -> type
        self.types_constructors: dict[str, list[BSType]] = {} # type_name -> list of constructors

    # pylint: disable-next = unused-private-member
    def __force_clear(self) -> None:
        """NEVER EVER run this method. It is required only for tests.
        """
        self.used_constructors: dict[str, BSType] = {} # constructor_name -> type
        self.types_constructors: dict[str, list[BSType]] = {} # type_name -> list of constructors
        # raise RuntimeWarning("Cleaned.")

    def has_constructor(self, constructor_name: str) -> BSType | None:
        """Returns type associated with constructor by its name or None
        if there is no defined constructor with this name

        Args:
            constructor_name (str): name of the constructor (in the scheme)

        Returns:
            BSType | None: BSType object or None if there is no type
            associated with given constructor name
        """
        return self.used_constructors.get(constructor_name, None)

    def crc32(self, data: str) -> str:
        """Calculates CRC32 hash of the given string.
        Please read Deserialization/Serialization section in the documentation
        if you don't understand what is it.

        Args:
            data (str): data

        Returns:
            str: 4 bytes of CRC32(data) - in the hex format
        """
        return hex(binascii.crc32(data.encode()) % (1 << 32))[2:]

    def _register_type(self, _type: BSType) -> None:
        """Internal function to associate the constructor by the type

        Args:
            type (BSType): new BSType you want to declare
        """
        self.used_constructors[_type.constructor_name] = _type
        # pylint: disable-next=protected-access
        if _type._name not in self.types_constructors:
            # pylint: disable-next=protected-access
            self.types_constructors[_type._name] = []
        # pylint: disable-next=protected-access
        self.types_constructors[_type._name].append(_type)

        # print("===")
        # print("Ok, type has been registered")
        # print(_type._name, "was added")
        # print(self.types_constructors[_type._name])
        # print("===")

    def get_constructors_of_type(self, type_name: str) -> list[BSType]:
        """Returns constructors associated with the type

        Args:
            type_name (str): type (not constructor or full name!) name

        Returns:
            list[BSType]: list of constructors
        """
        return self.types_constructors.get(type_name, [])

BS = BSMeta() # the one and only instance of BSMeta()


class BSType:
    """Base class for BSType objects. BSType is the constructor associated
    with type in the `---types---` combinators section.
    
    **Example**:
    ```bs
    user id: int = User;
    ```
    After this scheme parsing there will be created BSType with
    - `type_name` = `"User"`
    - `constructor_name` = `"user"`
    - `type_value` = `[BSParam(param_name="id", param_type=BSInt)]`
    """

    # pylint: disable-next = too-many-arguments
    def __init__(
        self,
        type_name: str,
        type_value: list[BSParam],
        constructor_name: str,
        is_builtin_type: bool = False,
        is_comlex_type = False,
        optional_types: set[BSType] | None = None) -> None:
        if (used_type := BS.has_constructor(constructor_name)) is not None:
            raise ValueError((
                f"Constructor with name {constructor_name} has already been "
                f"declared for type {used_type._name}.{used_type.constructor_name}#{used_type.hash}"
            ))
        self._name = type_name
        self.constructor_name = constructor_name
        self.params = type_value
        self.is_builtin_type = is_builtin_type
        self.is_comlex_type = is_comlex_type
        self.optional_types = optional_types

        # if type is complex (like int | null), we don't need to emphasize a constructor name
        if not self.is_comlex_type:
            BS._register_type(self)

    @property
    def hash(self) -> str:
        """CRC32 hash of the type constructor

        Returns:
            str: CRC32(self.convert_to_scheme())
        """
        if self.is_comlex_type:
            raise ValueError(f"Cannot calculate CRC32 from complex type {self.name}")
        # print("hash from", self.is_comlex_type, self.convert_to_scheme())
        return BS.crc32(self.convert_to_scheme())

    @property
    def name(self) -> str:
        """Returns the type name for showing in BSObject.__str__().
        If type is complex: all type variations joined by "|"
        If type is not complex:
            - `Type` (without constructor name) if there is only 
            one type constructor
            - `Type.constructor` if there are several constructors

        Returns:
            str: described above
        """
        if self.is_comlex_type:
            sorted_type_names: list[BSType] = list(sorted(
                self.optional_types,
                key=lambda _type: _type.name
            ))
            return " | ".join(_type.name for _type in sorted_type_names)

        variants = len(BS.get_constructors_of_type(self._name))
        # print(BS.get_constructors_of_type(self._name))
        return self._name if variants == 1 else f"{self._name}.{self.constructor_name}"

    def convert_to_scheme(self) -> str:
        """Generate string in the scheme notation

        Returns:
            str: scheme-notated definition
        """
        # print([param.type.optional_types for param in self.params][1])
        if self.is_comlex_type:
            return self.name
        types = ', '.join([
            f'{param.name}: {param.type.name}' for param in self.params
        ])
        return f"{self.constructor_name} {types} = {self._name}"

    def validate(self, data: object) -> bool:
        """You should implement validate() method for your type,
        which returns `True` if the method `to_BS_object` can be called
        with given data, or `False` if it can't.

        Args:
            data (object): data

        Returns:
            bool: can the BSObject be created from `data`
        """
        # print(f"Validating type {self.name}")
        # pylint: disable-next = protected-access
        if isinstance(data, BSObject) and self == data._type:
            return True
        validation_result = self._validate(data)
        # print(f"{self.name} validated: {validation_result}")
        return validation_result

    def _validate(self, data: object) -> bool:
        """Object validation

        Args:
            data (object): the Python object you want to validate

        Returns:
            bool: can the BSObject be created from `data`
        """
        if self.is_comlex_type:  # pylint: disable = no-else-return
            # complex type like int | null
            for _type in self.optional_types:
                if _type.validate(data):
                    return True
            return False
        else: # pylint: disable = no-else-return
            # simple type
            for param in self.params:
                if param.name not in data.keys():
                    return False
                if not param.type.validate(data[param.name]):
                    return False
            return True


    def to_BS_object(self, data: object) -> BSObject:
        """Use this method to convert Python object to BSObject.

        Args:
            data (object): Python object

        Raises:
            ValueError: raises if the given data can't be converted

        Returns:
            BSObject: created object
        """
        # pylint: disable-next = protected-access
        if isinstance(data, BSObject) and self == data._type:
            return data
        if not self.validate(data):
            raise ValueError((
                f"The provided Python object can't "
                f"be converted to type {self._name}.{self.constructor_name}#{self.hash}"
            ))
        return self._to_BS_object(data)

    def _to_BS_object(self, data: object) -> BSObject:
        """In this method you should implement convertor from Python object
        to BSObject of your type.
        Note that this method shouldn't be called directly, use 
        `type.to_BS_object()` with same signature instead.

        Args:
            data (object): Python object to convert
        """
        if self.is_comlex_type:  # pylint: disable = no-else-raise
            # complex type like int | null
            for _type in self.optional_types:
                if _type.validate(data):
                    return _type.to_BS_object(data)
            raise ValueError((
                "Given object cannot be casted to any of these types: "
                f"{' | '.join(self.optional_types)}"
            ))
        else:
            # simple type
            params_for_bs_object = {}
            for param in self.params:
                if param.name not in data.keys():
                    raise ValueError(
                        f"Given object does not contain required parameter {param.name}"
                    )
                params_for_bs_object[param.name] = param.type.to_BS_object(data[param.name])
            return BSObject[self](self, params_for_bs_object)

    def __or__(self, another_type: BSType) -> BSType:
        new_optional_types: set[BSType] = set()
        if self.is_comlex_type:
            new_optional_types |= self.optional_types
        else:
            new_optional_types.add(self)
        if another_type.is_comlex_type:
            new_optional_types |= another_type
        else:
            new_optional_types.add(another_type)
        if len(new_optional_types) == 1:
            return list(new_optional_types)[0]
        return BSType(
            type_name=f"{self.name} | {another_type.name}",
            type_value=[],
            constructor_name=f"complex_type<{self.name} | {another_type.name}>",
            is_builtin_type=False,
            is_comlex_type=True,
            optional_types=new_optional_types
        )

    def __eq__(self, another_type: BSType) -> bool:
        if not isinstance(another_type, BSType):
            # print("failed 1")
            # print(self, another_type)
            return False
        if self.is_comlex_type != another_type.is_comlex_type:
            # print("failed 2")
            return False
        if self.is_comlex_type and self.optional_types != another_type.optional_types:
            # print("failed 3")
            return False
        return True

    def __hash__(self):
        return int(self.hash, 16)

# pylint: disable-next=too-few-public-methods
class BSParam:
    """Base class for params in combinators
    """
    def __init__(self, param_name: str, param_type: BSType) -> None:
        self.name = param_name
        self.type = param_type


T = TypeVar("T", bound=BSType)

# pylint: disable-next=too-few-public-methods
class BSObject(Generic[T]):
    """Base BSObject class.
    """
    def __init__(self, _type: T, data: Any) -> None:
        self._type = _type
        self.data = data


    def __str__(self, tab_size=0):
        # params = "\n".join(
        #     [f"    {param.name}={str(param.value)}" for param in self.type.params]
        # )
        # if len(self.data.keys()) > 1:
        params = "\n".join(
            [
                (
                    f"{' ' * (tab_size + 4)}{key}="
                    f"{value.__str__(tab_size + 4) if isinstance(value, BSObject) else str(value)}"
                ) for key, value in self.data.items()
            ]
        )
        if self._type._name == "null":
            return "null"
        return (
            f"{self._type.name}(\n"
            f"{params}"
            f"\n{' ' * tab_size})"
        )


class _BSInt(BSType):
    name = "int"
    constructor_name = "int"
    params = []
    is_builtin_type = True
    # @override

    # def __init__(self, type_name: str, type_value: list[BSParam], constructor_name: str) -> None:

    def __init__(self) -> None:
        super().__init__(
            type_name=self.name,
            type_value=self.params,
            constructor_name=self.constructor_name,
            is_builtin_type=self.is_builtin_type
        )
    def convert_to_scheme(self) -> str:
        return self.name

    def _validate(self, data: object) -> bool:
        return isinstance(data, int)

    def _to_BS_object(self, data: object) -> BSObject:
        return BSObject[self](self, {
            "value": int(data)
        })

class _BSStr(BSType):
    name = "str"
    constructor_name = "str"
    params = []
    is_builtin_type = True
    # @override

    # def __init__(self, type_name: str, type_value: list[BSParam], constructor_name: str) -> None:

    def __init__(self) -> None:
        super().__init__(
            type_name=self.name,
            type_value=self.params,
            constructor_name=self.constructor_name,
            is_builtin_type=self.is_builtin_type
        )
    def convert_to_scheme(self) -> str:
        return self.name

    def _validate(self, data: object) -> bool:
        return isinstance(data, str)

    def _to_BS_object(self, data: object) -> BSObject:
        return BSObject[self](self, {
            "value": "".join(data)
        })

class _BSNull(BSType):
    name = "null"
    constructor_name = "null"
    params = []
    is_builtin_type = True
    # @override

    # def __init__(self, type_name: str, type_value: list[BSParam], constructor_name: str) -> None:

    def __init__(self) -> None:
        super().__init__(
            type_name=self.name,
            type_value=self.params,
            constructor_name=self.constructor_name,
            is_builtin_type=self.is_builtin_type
        )
    def convert_to_scheme(self) -> str:
        return self.name

    def _validate(self, data: object) -> bool:
        return data is None

    def _to_BS_object(self, data: object = None) -> BSObject:
        return BSObject[self](self, {})

BSInt = _BSInt()
BSStr = _BSStr()
BSNull = _BSNull()
