from vkwave.bots import BaseEvent
from vkwave.bots.core.dispatching.filters.builtin import get_text

from state_manager.filters.base import BaseTextFilter, BaseTextContainsFilter, BaseRegexFilter
from state_manager.filters.logic import text_in_list, text_contains, text_matches_regex


class TextFilter(BaseTextFilter):
    def check(self, event: BaseEvent) -> bool:
        text = get_text(event)
        if text is None:
            return False
        if self.ignore_case:
            text = text.lower()

        return text_in_list(text, self.text)


class TextContainsFilter(BaseTextContainsFilter):
    def check(self, event: BaseEvent) -> bool:
        text = get_text(event)
        if text is None:
            return False
        if self.ignore_case:
            text = text.lower()

        return text_contains(text, self.text)


class RegexFilter(BaseRegexFilter):
    def check(self, event: BaseEvent) -> bool:
        text = get_text(event)
        if text is None:
            return False
        return text_matches_regex(text, self.pattern)


text_filter = TextFilter
text_contains_filter = TextContainsFilter
regex_filter = RegexFilter
