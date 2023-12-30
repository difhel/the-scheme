"""
Tests for correct equality of types
"""
from core.builtins import BSType, BSParam, BSObject, BSStr, BSInt, BSNull, BS


def test_builtin_types():
    assert BSInt == BSInt
    assert BSStr == BSStr
    assert BSNull == BSNull


def test_complex_type_subtype_order():
    assert BSInt | BSNull == BSNull | BSInt
    # also assert BS
    assert (BSInt | BSNull).convert_to_scheme() == (BSNull | BSInt).convert_to_scheme()

def test_fake_complex_type_collapse():
    BS._BSMeta__force_clear()
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
    BS._BSMeta__force_clear()