from state_manager.types.generals import AnyText


def text_in_list(text: str, list: AnyText) -> bool:
    return text in list


def text_contains(text: str, list: AnyText) -> bool:
    for word in list:
        if word in text:
            return True
    return False


def text_matches_regex(text: str, pattern) -> bool:
    return pattern.match(text) is not None
