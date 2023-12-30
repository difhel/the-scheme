"""
Tests for correct equality of types
"""
from core.builtins import BSType, BSParam, BSObject, BSStr, BSInt, BSNull


def test_builtin_types():
    assert BSInt == BSInt
    assert BSStr == BSStr
    assert BSNull == BSNull


def test_complex_type_subtype_order():
    assert BSInt | BSNull == BSNull | BSInt
    # also assert BS
    assert (BSInt | BSNull).convert_to_scheme() == (BSNull | BSInt).convert_to_scheme()

def test_fake_complex_type_collapse():
    assert BSInt | BSInt == BSInt
    assert (BSInt | BSInt | BSInt) == BSInt
    # also assert hashes
    assert (BSInt | BSInt).hash == BSInt.hash
    assert (BSInt | BSInt | BSInt).hash == BSInt.hash