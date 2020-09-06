from logging import getLogger
from typing import Optional, Tuple, Callable

from state_manager.handlers.base import BaseStateHandler, BaseHandler
from state_manager.types.generals import Filter, Filters

logger = getLogger(__name__)


class AiogramStateHandler(BaseStateHandler):
    def default_handler_logic(
        self, event_type: str, filters: Filters, state_name: Optional[str] = None
    ) -> Callable:
        def wrap(callback: Callable):
            self.registration_state_handler(event_type, callback, state_name=state_name, filters=filters)
            return callback

        return wrap

    def message_handler(self, *filters: Filter, state_name: Optional[str] = None) -> Callable:
        return self.default_handler_logic("message", filters, state_name)

    def callback_query_handler(self, *filters: Filter, state_name: Optional[str] = None) -> Callable:
        return self.default_handler_logic("callback_query", filters, state_name)

    def edited_message_handler(self, *filters: Filter, state_name: Optional[str] = None) -> Callable:
        return self.default_handler_logic("edited_message", filters, state_name)

    def channel_post_handler(self, *filters: Filter, state_name: Optional[str] = None) -> Callable:
        return self.default_handler_logic("channel_post", filters, state_name)

    def edited_channel_post_handler(self, *filters: Filter, state_name: Optional[str] = None) -> Callable:
        return self.default_handler_logic("edited_channel_post", filters, state_name)


class AiogramHandler(BaseHandler):
    def default_handler_logic(self, event_type: str, filters: Filters) -> Callable:
        def wrap(callback: Callable):
            self.registration_handler(event_type, callback, filters=filters)
            return callback

        return wrap

    def message_handler(self, *filters: Filter) -> Callable:
        return self.default_handler_logic("message", filters)

    def callback_query_handler(self, *filters: Filter) -> Callable:
        return self.default_handler_logic("callback_query", filters)

    def edited_message_handler(self, *filters: Filter) -> Callable:
        return self.default_handler_logic("edited_message", filters)

    def channel_post_handler(self, *filters: Filter) -> Callable:
        return self.default_handler_logic("channel_post", filters)

    def edited_channel_post_handler(self, *filters: Filter) -> Callable:
        return self.default_handler_logic("edited_channel_post", filters)
