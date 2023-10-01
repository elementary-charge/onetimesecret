from fastapi import (
    HTTPException,
)


class NoSecretException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=401,
            detail='It either never existed or has already been viewed',
        )


class RateLimitException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=429,
            detail='Too many requests, dude!',
        )
