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
        {
            "code": "err_1",
            "message": "err_1",
        },
        {
            "code": "err_2",
            "message": "err_2",
            "args": {"str_arg": "ok"},
        },
        {
            "code": "err_3",
            "message": "err_3",
            "args": {"int_arg": 42},
        },
        {
            "code": "err_4",
            "message": "err_4",
            "args": {"float_arg": 42.0},
        },
    ]


def test_complex_error_formatting():
    formatter = JSONErrorFormatter()

    errors = [
        Error(
            "err_1",
            {
                "value_1": Error("value_1_err"),
                "value_2": Error("value_2_err"),
            },
        ),
    ]

    assert formatter.format(errors) == [
        {
            "code": "err_1",
            "message": "err_1",
            "args": {
                "value_1": {"code": "value_1_err", "message": "value_1_err"},
                "value_2": {"code": "value_2_err", "message": "value_2_err"},
            },
        },
    ]


def test_unexpected_type_of_error_argument():
    formatter = JSONErrorFormatter()

    with pytest.raises(ValueError):
        formatter.format(
            [
                Error("err", {"arg": set()}),
            ]
        )
