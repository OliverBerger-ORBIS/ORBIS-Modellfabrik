
reset_requested = None
ResetException = None


def reset_init():
    global reset_requested, ResetException
    reset_requested = False
    ResetException = reset_get_ResetException()


def reset_get_ResetException():
    global reset_requested, ResetException
    if ResetException is None:
        class ResetException(Exception):
                "Raised when the the current action is aborted due to a reset"
                pass
    return ResetException


def reset_set_request():
    global reset_requested, ResetException
    reset_requested = True


def reset_clear_request():
    global reset_requested, ResetException
    reset_requested = False


def reset_raise_exception_if_requested():
    global reset_requested, ResetException
    if reset_requested:
        reset_clear_request()
        raise ResetException()
