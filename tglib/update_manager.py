#!/bin/python3

import os
import inspect
from typing import (Any,
                    Union,
                    Callable)

from .logger import get_logger
logger = get_logger('TelegramApi')

__all__ = [
    '_run_coroutine',
    'UpdateManager',
    'NextManager',
    # aliases
    'MESSAGE_MANAGER',
    'EDITED_MESSAGE_MANAGER',
    'CHANNEL_POST_MANAGER',
    'EDITED_CHANNEL_POST_MANAGER',
    'MESSAGE_REACTION_MANAGER',
    'MESSAGE_REACTION_COUNT_MANAGER',
    'INLINE_QUERY_MANAGER',
    'CHOSEN_INLINE_RESULT_MANAGER',
    'CALLBACK_QUERY_MANAGER',
    'SHIPPING_QUERY_MANAGER',
    'PRE_CHECKOUT_QUERY_MANAGER',
    'POLL_MANAGER',
    'POLL_ANSWER_MANAGER',
    'MY_CHAT_MEMBER_MANAGER',
    'CHAT_MEMBER_MANAGER',
    'CHAT_JOIN_REQUEST_MANAGER',
    'CHAT_BOOST_MANAGER',
    'REMOVED_CHAT_BOOST_MANAGER'
]

MESSAGE_MANAGER = 'message_manager'
EDITED_MESSAGE_MANAGER = 'edited_message_manager'
CHANNEL_POST_MANAGER = 'channel_post_manager'
EDITED_CHANNEL_POST_MANAGER = 'edited_channel_post_manager'
MESSAGE_REACTION_MANAGER = 'message_reaction_manager'
MESSAGE_REACTION_COUNT_MANAGER = 'message_reaction_count_manager'
INLINE_QUERY_MANAGER = 'inline_query_manager'
CHOSEN_INLINE_RESULT_MANAGER = 'chosen_inline_result_manager'
CALLBACK_QUERY_MANAGER = 'callback_query_manager'
SHIPPING_QUERY_MANAGER = 'shipping_query_manager'
PRE_CHECKOUT_QUERY_MANAGER = 'pre_checkout_query_manager'
POLL_MANAGER = 'poll_manager'
POLL_ANSWER_MANAGER = 'poll_answer_manager'
MY_CHAT_MEMBER_MANAGER = 'my_chat_member_manager'
CHAT_MEMBER_MANAGER = 'chat_member_manager'
CHAT_JOIN_REQUEST_MANAGER = 'chat_join_request_manager'
CHAT_BOOST_MANAGER = 'chat_boost_manager'
REMOVED_CHAT_BOOST_MANAGER = 'removed_chat_boost_manager'

examples = {
    MESSAGE_MANAGER : "lambda message: message.chat.id == xyz",
    EDITED_MESSAGE_MANAGER : "lambda message: message.chat.id == xyz",
    CHANNEL_POST_MANAGER : "lambda message: message.chat.id == xyz",
    EDITED_CHANNEL_POST_MANAGER : "lambda message: message.chat.id == xyz",
    MESSAGE_REACTION_MANAGER: "lambda message_reaction: message_reaction.chat.id == xyz",
    MESSAGE_REACTION_COUNT_MANAGER: "lambda message_reaction_count: message_reaction_count.chat.id == xyz",
    INLINE_QUERY_MANAGER : "lambda inline_query: inline_query.from_user.id == xyz",
    CHOSEN_INLINE_RESULT_MANAGER : "lambda chosen_inline_result: chosen_inline_result.from_user.id == xyz",
    CALLBACK_QUERY_MANAGER : "lambda callback_query: callback_query.from_user.id == xyz",
    SHIPPING_QUERY_MANAGER : "lambda shipping_query: shipping_query.from_user.id == xyz",
    PRE_CHECKOUT_QUERY_MANAGER : "lambda pre_checkout_query: pre_checkout_query.from_user.id == xyz",
    POLL_MANAGER : "lambda poll: poll.id == xyz",
    POLL_ANSWER_MANAGER : "lambda poll_answer: poll_answer.poll_id == xyz",
    MY_CHAT_MEMBER_MANAGER : "lambda my_chat_member: my_chat_member.chat.id == xyz",
    CHAT_MEMBER_MANAGER : "lambda chat_member: chat_member.chat.id == xyz",
    CHAT_JOIN_REQUEST_MANAGER : "lambda chat_join_request: chat_join_request.chat.id == xyz",
    CHAT_BOOST_MANAGER: "lambda chat_boost: chat_boost.chat.id == xyz",
    REMOVED_CHAT_BOOST_MANAGER: "lambda removed_chat_boost: removed_chat_boost.chat.id == xyz"
}


def _func_ok(
    __func: Callable,
    /,
    *,
    must_be_coro: bool = False
) -> bool:

    if not inspect.isfunction(__func):
        return False

    spec = inspect.getfullargspec(__func)

    if (
        len(spec.args) == 1
        and not spec.varargs
        and not spec.varkw
        and not spec.kwonlyargs
    ):
        if (
            must_be_coro
            and inspect.iscoroutinefunction(__func)
        ):
            return True

        elif (
            not must_be_coro
            and not inspect.iscoroutinefunction(__func)
            and not inspect.isasyncgenfunction(__func)
            and not inspect.isgeneratorfunction(__func)
        ):
            return True

    return False


def _check_rule(
    __manager: str,
    __obj: Any,
    __checker: Callable,
    __function: Callable,
    /
) -> None:

    errors = []
    obj_name: str = __obj.__name__

    if not _func_ok(__checker):
        errors.append(
            "ERROR 1 • The 'checker' argument must"
            ' be a normal function that takes only'
            ' one parameter, it will be processed as'
            f' {obj_name}. E.g. -> {examples[__manager]}'
        )
    if not _func_ok(
        __function,
        must_be_coro = True
    ):
        n = len(errors) + 1
        errors.append(
            f'ERROR {n} • The wrapped function must be'
            ' an async def (async generator is not allowed)'
            ' that takes only one argument. E.g. -> async def'
            f' foo({obj_name.lower()}: {obj_name}): return ...'
        )
    if errors:
        len_err = len(errors)
        s = str() if len_err == 1 else 's'
        raise TypeError(
            f'{len_err} error{s} occurred while trying'
            f' to add a rule to the {__manager}, see below'
            f' for more details.\n\n' + '\n'.join(errors)
        )


class Rule:
    def __init__(
        self,
        __checker: Callable[[Any], Any],
        __function: Callable[[Any], Any],
        /
    ):
        self.__checker = __checker
        self.__function = __function

    @property
    def checker(self) -> Callable[[Any], Any]:
        return self.__checker

    @property
    def function(self) -> Callable[[Any], Any]:
        return self.__function


class NextManager:
    """
    A new update will be processed by the next manager returning
    the instance of this class in your decorated functions.
    """


async def _run_coroutine(
    __rule: Rule,
    __obj: Any,
    /
) -> Union[Any, NextManager]:

    try:
        check = __rule.checker(__obj)
    except BaseException as exc:
        code = __rule.checker.__code__
        lineno = code.co_firstlineno
        filename = os.path.basename(code.co_filename)
        logger.error(
            f'{exc!r} occurred in the'
            f' function {__rule.checker.__name__!r} in'
            f' file {filename!r} at line {lineno}.'
        )
        raise exc

    if not check:
        return NextManager()
    else:
        try:
            return await __rule.function(__obj)
        except BaseException as exc:
            code = __rule.function.__code__
            lineno = code.co_firstlineno
            filename = os.path.basename(code.co_filename)
            logger.error(
                f'{exc!r} occurred in the'
                f' function {__rule.function.__name__!r} in'
                f' file {filename!r} at line {lineno}.'
            )
            raise exc


class UpdateManager:
    def __init__(self, __name: str, __obj: Any, /):
        self.__name = __name
        self.__obj = __obj
        self.__rules = ()

    @property
    def rules(self) -> tuple[Rule]:
        return self.__rules

    def __iter__(self):
        self.__index = 0
        self.__end = len(self.rules)
        return self

    def __next__(self):
        if self.__index == self.__end:
            raise StopIteration
        self.__index += 1
        return self.rules[self.__index - 1]

    def add_rule(
        self,
        __checker: Callable[[Any], Any],
        __function: Callable[[Any], Any],
        /
    ) -> None:
        _check_rule(
            self.__name,
            self.__obj,
            __checker,
            __function
        )
        self.__rules += (Rule(__checker, __function), )
