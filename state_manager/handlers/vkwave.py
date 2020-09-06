from logging import getLogger
from typing import Optional, Callable

from state_manager.handlers.base import BaseStateHandler, BaseHandler
from state_manager.types.generals import Filters, Filter

logger = getLogger(__name__)


class VkWaveStateHandler(BaseStateHandler):
    def default_handler_logic(
        self, event_type: str, filters: Filters, state_name: Optional[str] = None
    ) -> Callable:
        def wrap(callback: Callable):
            self.registration_state_handler(event_type, callback, state_name=state_name, filters=filters)
            return callback

        return wrap

    def message_handler(self, *filters: Filter, state_name: Optional[str] = None) -> Callable:
        return self.default_handler_logic("message", filters, state_name)


class VkWaveHandler(BaseHandler):
    def default_handler_logic(self, event_type: str, filters: Filters) -> Callable:
        def wrap(callback: Callable):
            self.registration_handler(event_type, callback, filters=filters)
            return callback

        return wrap

    def message_handler(self, *filters: Filter) -> Callable:
        return self.default_handler_logic("message", filters)

