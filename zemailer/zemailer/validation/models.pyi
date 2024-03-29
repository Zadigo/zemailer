from functools import cached_property


class EmailEvaluationMixin:
    evaluation: set = ...
    mx_records: set = ...
    messages: list = ...
    errors: dict = ...
    @property
    def is_risky(self) -> bool: ...
    def get_json_response(self) -> dict: ...
    def add_error(self, error: str) -> None: ...
    def add_mx_records(self, records: list) -> None: ...
    def add_message(self, host: str, code: int, message: str) -> None: ...


class EmailAddress(EmailEvaluationMixin):
    def __init__(self, email: str) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    @cached_property
    def get_literal_ip(self) -> str: ...
    @cached_property
    def restructure(self) -> str: ...
