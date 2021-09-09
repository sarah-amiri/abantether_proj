class AccountException(Exception):
    pass


class InsufficientBalanceException(AccountException):
    pass


class InactiveAccountException(AccountException):
    pass


class NotFoundAccountException(AccountException):
    pass


class AmountInvalidException(AccountException):
    pass


class AccountsInvalidException(AccountException):
    pass
