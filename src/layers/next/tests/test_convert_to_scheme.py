"""
Tests for correct converting to the scheme format
"""
from core.builtins import BSType, BSParam, BSObject, BSStr, BSInt, BSNull, BS


def test_builtin_types():
    assert BSInt.convert_to_scheme() == "int"
    assert BSStr.convert_to_scheme() == "str"
    assert BSNull.convert_to_scheme() == "null"

def test_simple_custom_types():
    BS._BSMeta__force_clear()
    user_type = BSType(
        "User", [
            BSParam("id", BSInt),
            BSParam("first_name", BSStr | BSNull)
        ],
        "user"
    )
    assert user_type.convert_to_scheme() == "user id: int, first_name: null | str = User"
    bot_unused_type = BSType(
        "UnusedType", [
            BSParam("id", BSInt),
            BSParam("first_name", BSStr | BSNull),
            BSParam("bot_creator", user_type)
        ],
        "botUnused"
    )
    # test that if we have two constructors for one type (User.user and User.bot) we should specify exactly what constructor we want to use
    assert bot_unused_type.convert_to_scheme() == "botUnused id: int, first_name: null | str, bot_creator: User = UnusedType"
    bot_used_type = BSType(
        "User", [
            BSParam("id", BSInt),
            BSParam("first_name", BSStr | BSNull),
            BSParam("bot_creator", user_type)
        ],
        "bot"
    )
    assert bot_used_type.convert_to_scheme() == "bot id: int, first_name: null | str, bot_creator: User.user = User"
    BS._BSMeta__force_clear()
