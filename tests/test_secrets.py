from fastapi.testclient import TestClient

import settings


def test_secrets_proper(
    web_client: TestClient,
):
    # Сгенерируем ключ
    response = web_client.post(
        '/generate',
        json={
            'passphrase': 'my passphrase',
            'secret': 'my secret',
        },
    )
    result = response.json()
    secret_key = result.get('secret_key')
    assert isinstance(secret_key, str)
    assert len(secret_key) == 21
    # Попытаемся прочитать секрет c неверной кодовой фразой
    response = web_client.post(
        f'/secrets/{secret_key}',
        json={
            'passphrase': 'my mistake',
        },
    )
    assert response.status_code == 401
    result = response.json()
    detail = result.get('detail')
    assert detail == 'It either never existed or has already been viewed'
    # Прочитаем секрет на самом деле
    response = web_client.post(
        f'/secrets/{secret_key}',
        json={
            'passphrase': 'my passphrase',
        },
    )
    result = response.json()
    secret = result.get('secret')
    assert isinstance(secret, str)
    assert secret == 'my secret'
    # Прочитаем секрет повторно (нет)
    response = web_client.post(
        f'/secrets/{secret_key}',
        json={
            'passphrase': 'my passphrase',
        },
    )
    assert response.status_code == 401
    result = response.json()
    detail = result.get('detail')
    assert detail == 'It either never existed or has already been viewed'


def test_secrets_wrong(
    web_client: TestClient,
):
    # Сгенерируем ключ без кодовой фразы
    response = web_client.post(
        '/generate',
        json={
            'secret': 'my secret',
        },
    )
    assert response.status_code == 422
    result = response.json()
    detail = result.get('detail')
    assert isinstance(detail, list)
    assert detail
    msg = detail[0].get('msg')
    assert msg == 'Field required'
    # Сгенерируем ключ на пустую кодовую фразу
    response = web_client.post(
        '/generate',
        json={
            'passphrase': '',
            'secret': 'my secret',
        },
    )
    assert response.status_code == 422
    result = response.json()
    detail = result.get('detail')
    assert isinstance(detail, list)
    assert detail
    msg = detail[0].get('msg')
    assert msg == 'String should have at least 1 characters'


def test_secrets_too_many_requests(
    web_client: TestClient,
):
    # Сгенерируем ключ
    response = web_client.post(
        '/generate',
        json={
            'passphrase': 'my passphrase',
            'secret': 'my secret',
        },
    )
    result = response.json()
    secret_key = result.get('secret_key')
    assert isinstance(secret_key, str)
    # Попытаемся подобрать кодовую фразу
    response = None
    for i in range(settings.RATE_LIMIT_PER_MINUTE + 1):
        response = web_client.post(
            f'/secrets/{secret_key}',
            json={
                'passphrase': f'my passphrase {i}',
            },
        )
        if response.status_code == 429:
            assert i == settings.RATE_LIMIT_PER_MINUTE
    assert response is not None
    assert response.status_code == 429
    result = response.json()
    detail = result.get('detail')
    assert detail == 'Too many requests, dude!'
