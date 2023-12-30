"""
Tests for correct equality of types
"""
from core.builtins import BSType, BSParam, BSStr, BSInt, BSNull, BS


def test_builtin_types():
    """
    Testing `__eq__` for built-in types
    """
    assert BSInt == BSInt  # pylint: disable = comparison-with-itself
    assert BSStr == BSStr  # pylint: disable = comparison-with-itself
    assert BSNull == BSNull  # pylint: disable = comparison-with-itself


def test_complex_type_subtype_order():
    """
    Testing that complex types with different subtypes order
    are equal (because of `optional_types: set[BSType]` and
    sorting params by their names while converting to BS)
    """
    assert BSInt | BSNull == BSNull | BSInt
    # also assert BS
    assert (BSInt | BSNull).convert_to_scheme() == (BSNull | BSInt).convert_to_scheme()

def test_fake_complex_type_collapse():
    """
    Testing that fake complex types (like `int | int`) collapse
    to the simple type
    """
    BS._BSMeta__force_clear()  # pylint: disable=protected-access
    assert BSInt | BSInt == BSInt
    assert (BSInt | BSInt | BSInt) == BSInt
    # also assert hashes
    assert (BSInt | BSInt).hash == BSInt.hash
    assert (BSInt | BSInt | BSInt).hash == BSInt.hash

    # test it on custom types
    user_type = BSType(
        "User", [
            BSParam("id", BSInt),
            BSParam("first_name", BSStr | BSNull),
            BSParam("bot_creator", BSInt)
        ],
        "bot"
    )
    assert (user_type | user_type) == user_type
    assert (user_type | user_type | user_type) == user_type
    assert (user_type | user_type).convert_to_scheme() == user_type.convert_to_scheme()
    BS._BSMeta__force_clear()  # pylint: disable=protected-access
