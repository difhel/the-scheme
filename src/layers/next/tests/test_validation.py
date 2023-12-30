"""
Tests for type validation
"""
from core.builtins import BSType, BSParam, BSObject, BSStr, BSInt, BSNull, BS

def test_builtin_types():
    # BSInt
    assert BSInt.validate(42)
    assert BSInt.validate(BSInt.to_BS_object(42))
    assert not BSInt.validate("42")
    assert not BSInt.validate(None)
    assert BSInt.validate(True) # Python bool is subclass of int :-(
    
    # BSStr
    assert BSStr.validate("magic")
    assert BSStr.validate(BSStr.to_BS_object("magic"))
    assert BSStr.validate("")
    assert not BSStr.validate(None)
    assert not BSStr.validate(True)
    assert not BSStr.validate([])
    
    # BSNull
    assert BSNull.validate(None)
    assert BSNull.validate(BSNull.to_BS_object(None))

def test_complex_types():
    optional_int = BSInt | BSNull
    assert optional_int.validate(42)
    assert optional_int.validate(BSInt.to_BS_object(42))
    assert optional_int.validate(None)
    assert optional_int.validate(BSNull.to_BS_object(None))

def test_simple_custom_types():
    # testing recursion validation
    BS._BSMeta__force_clear()
    user_type = BSType(
        "User", [
            BSParam("id", BSInt),
            BSParam("first_name", BSStr | BSNull)
        ],
        "user"
    )
    assert user_type.validate({
        "id": 42,
        "first_name": "Mark"
    })
    assert user_type.validate({
        "id": 42,
        "first_name": None
    })
    assert not user_type.validate({
        "id": "42",
        "first_name": None
    })
    assert not user_type.validate({
        "id": 42,
        "first_name": 42
    })
    assert not user_type.validate({
        "id": 42
    })
    assert not user_type.validate({})
    BS._BSMeta__force_clear()