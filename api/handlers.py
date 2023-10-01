from fastapi import (
    APIRouter,
)

from api import (
    schemas,
    exceptions,
)
from db.models import (
    Secret,
)
from api.services import (
    generate_secret_key,
    DEFAULT_PASSPHRASE_HASH,
    hash_passphrase,
    verify_passphrase,
    encrypt_secret,
    decrypt_secret,
)


router = APIRouter()


@router.post(
    '/generate',
    response_model=schemas.GenerateSecretResponse,
)
async def generate_secret_handler(
    data: schemas.GenerateSecretRequest,
):
    """
    Метод принимает секрет и кодовую фразу, а
    отдает ключ по которому этот секрет можно получить

    """
    secret_key = generate_secret_key()
    passphrase_hash = hash_passphrase(data.passphrase)
    secret_hash = encrypt_secret(data.secret, data.passphrase)
    doc = Secret(
        secret_key=secret_key,
        passphrase_hash=passphrase_hash,
        secret_hash=secret_hash,
    )
    await doc.insert()
    return schemas.GenerateSecretResponse(
        secret_key=secret_key,
    )


@router.post(
    '/secrets/{secret_key}',
    response_model=schemas.GetSecretResponse,
)
async def get_secret_handler(
    secret_key: str,
    data: schemas.GetSecretRequest,
):
    """
    Метод принимает кодовую фразу, и отдает секрет,
    если кодовая фраза верна

    После однократного вычисления секрета, запись в БД сгорает

    """
    doc = await Secret.find_one(Secret.secret_key == secret_key)
    passphrase_hash = (
        # Значение хеша по-умолчанию используется
        # как защита от атаки на подбор существующих ключей
        # Делается допущение, что без вызова алгоритма проверки кодовой фразы
        # среднее время ответа может быть меньше
        doc.passphrase_hash
        if doc is not None
        else DEFAULT_PASSPHRASE_HASH
    )
    passphrase_check = verify_passphrase(passphrase_hash, data.passphrase)
    if doc is None:
        # Логически эта проверка здесь не обязательна
        # Она написана для самоуспокоения и избежания потенциальных багов
        raise exceptions.NoSecretException
    if not passphrase_check:
        raise exceptions.NoSecretException
    secret = decrypt_secret(doc.secret_hash, data.passphrase)
    await doc.delete()
    return schemas.GetSecretResponse(
        secret=secret,
    )
