import pytest

from goodboy.errors import Error, JSONErrorFormatter


def test_simple_error_formatting():
    formatter = JSONErrorFormatter()

    errors = [
        Error("err_1"),
        Error("err_2", {"str_arg": "ok"}),
        Error("err_3", {"int_arg": 42}),
        Error("err_4", {"float_arg": 42.0}),
    ]

    assert formatter.format(errors) == [
        {"code": "err_1"},
        {
            "code": "err_2",
            "args": {"str_arg": "ok"},
        },
        {
            "code": "err_3",
            "args": {"int_arg": 42},
        },
        {
            "code": "err_4",
            "args": {"float_arg": 42.0},
        },
    ]


def test_complex_error_formatting():
    formatter = JSONErrorFormatter()

    errors = [
        Error(
            "values_error",
            {
                "value_1": Error("cannot_be_none"),
                "value_2": Error("cannot_be_none"),
            },
        ),
    ]

    assert formatter.format(errors) == [
        {
            "code": "values_error",
            "args": {
                "value_1": {
                    "code": "cannot_be_none",
                },
                "value_2": {
                    "code": "cannot_be_none",
                },
            },
        },
    ]


def test_unexpected_type_of_error_argument():
    formatter = JSONErrorFormatter()

    with pytest.raises(ValueError):
        formatter.format(
            [
                Error("err", {"arg": []}),
            ]
        )
