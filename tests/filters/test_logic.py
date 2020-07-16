from state_manager.filters.logic import text_in_list, text_contains


def test_text_in_list():
    assert text_in_list("111", ["111", "222"])
    assert not text_in_list("111", ["222", "333"])


def test_text_contains():
    assert text_contains("123 123", ["123"])
    assert not text_contains("123 123", ["234"])
