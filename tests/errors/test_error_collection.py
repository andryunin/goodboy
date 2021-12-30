from goodboy.errors import Error, ErrorCollection


def test_append_method():
    error = Error("oops")

    collection = ErrorCollection()
    collection.append(error)

    assert list(collection) == [error]


def test_append_error_method():
    code = "oops"
    args = {"foo": "bar"}
    nested_errors = {"baz": Error("baz_oops")}

    error = Error(code, args, nested_errors, "oops")

    collection = ErrorCollection()
    collection.append_error(code, args, nested_errors)

    print(repr(error))
    print(repr(collection[0]))

    assert error == collection[0]


def test_concat_collections():
    error_1 = Error("foo")
    collection_1 = ErrorCollection([error_1])

    error_2 = Error("bar")
    collection_2 = ErrorCollection([error_2])

    assert list(collection_1 + collection_2) == [error_1, error_2]
