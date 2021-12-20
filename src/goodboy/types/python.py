from goodboy.schema import Schema


class CallableValue(Schema):
    """
    Accept callable python objects.

    :param allow_none: If true, value is allowed to be ``None``.
    :param messages: Override error messages.
    :param rules: Custom validation rules.
    """

    def validate(self, value, typecast: bool, context: dict = {}):
        errors = []

        if not callable(value):
            errors.append(self.error("not_callable"))

        value, rule_errors = self.call_rules(value, typecast, context)

        return value, errors + rule_errors

    def typecast(self, input, context: dict = {}):
        return input, []
