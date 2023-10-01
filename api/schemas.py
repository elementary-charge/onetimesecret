from typing import (
    Annotated,
)

from pydantic import (
    BaseModel,
    Field,
)


class GenerateSecretRequest(BaseModel):
    passphrase: Annotated[str, Field(min_length=1)]
    secret: str


class GenerateSecretResponse(BaseModel):
    secret_key: str


class GetSecretRequest(BaseModel):
    passphrase: str


class GetSecretResponse(BaseModel):
    secret: str
