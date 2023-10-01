from fastapi import (
    FastAPI,
    Request,
)
from fastapi.exception_handlers import http_exception_handler
from motor.motor_asyncio import (
    AsyncIOMotorClient,
)
from beanie import (
    init_beanie,
)
from ratelimit import (
    RateLimitMiddleware,
    Rule,
)
from ratelimit.backends.simple import MemoryBackend
from ratelimit.types import (
    Scope,
    Receive,
    Send,
    ASGIApp,
)

import settings
from api.handlers import router
from api.exceptions import (
    RateLimitException,
)
from db.models import (
    Secret,
)

app = FastAPI()


async def _auth_function(_: Scope) -> tuple[str, str]:
    # Все пользователи поразительно на одно лицо!
    return 'default', 'default'


def _on_blocked(_: int) -> ASGIApp:
    async def asgi_app(scope: Scope, receive: Receive, send: Send) -> None:
        # Штатный механизм обработки исключений fastapi
        # не перехватывает исключения в миддлварах
        # Поэтому здесь представлена реализация перехвата по мотивам оригинала
        request = Request(scope, receive, send)
        response = await http_exception_handler(request, RateLimitException())
        await response(scope, receive, send)
    return asgi_app


app.add_middleware(
    RateLimitMiddleware,
    authenticate=_auth_function,
    backend=MemoryBackend(),
    config={
        r"^/.*": [
            Rule(minute=settings.RATE_LIMIT_PER_MINUTE),
        ],
    },
    on_blocked=_on_blocked,
)


async def init_mongodb():
    document_models = [
        Secret,
    ]
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client.get_database(settings.MONGO_DATABASE)
    await init_beanie(
        database=db,
        document_models=document_models,
    )


@app.on_event('startup')
async def startup_event():
    await init_mongodb()
    app.include_router(router)
