class AccountException(Exception):
    pass


class InsufficientBalanceException(AccountException):
    pass


class InactiveAccountException(AccountException):
    pass
