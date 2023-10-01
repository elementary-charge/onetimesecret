from beanie import (
    Document,
    Indexed,
)


class Secret(Document):
    secret_key: Indexed(str, unique=True)
    passphrase_hash: str
    secret_hash: str
