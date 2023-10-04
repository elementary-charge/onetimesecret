В качестве тестового задания нужно сделать REST сервис для одноразовых секретов наподобие https://onetimesecret.com/

Он должен позволить создать секрет, задать кодовую фразу для его открытия и cгенерировать код, по которому можно прочитать секрет только один раз. UI не нужен, это должен быть JSON Api сервис.

Для написания сервиса можно использовать FastAPI или другой фреймворк.

- Метод `/generate` должен принимать секрет и кодовую фразу и отдавать `secret_key` по которому этот секрет можно получить.

- Метод `/secrets/{secret_key}` принимает на вход кодовую фразу и отдает секрет.

- Данные сервиса хранятся в базе данных. Можно использовать Postgres или MongoDB.

- Сервис должен использовать Docker и запускаться с помощью `docker-compose up`. Запуск БД также описан в `docker-compose`.


__Требования:__

- Требований к используемым технологиям нет.

- Сервис асинхронно обрабатывает запросы.

- Секреты и кодовые фразы не хранятся в базе в открытом виде.

- Код должен соответствовать PEP, необходимо использование type hints, к публичным методам должна быть написана документация.

- Написаны тесты (постарайтесь достичь покрытия в 70% и больше). Вы можете использовать pytest или любую другую библиотеку для тестирования

- Сервис должен корректно обрабатывать валидные и невалидные входящие запросы и выдавать соответствующие HTTP статусы


__*Дополнительно (по желанию)__

- Добавить возможность ограничения количества запросов (напр., 600 в минуту). При превышении лимита, сервер должен возвращать статус «429 Too Many Requests»

- Разместить образ контейнера на Docker Hub для возможности независимой установки на другой машине (все сервисы должны развернуться стандартной командой)

- Взаимодействие с БД можете реализовать асинхронно


__Запуск сервиса и тестов__

Требуется наличие docker, docker-compose

Поднять сервис и необходимые БД можно командой `docker-compose up`
Тесты запустятся автоматически и однократно

Сервис поднимается на localhost на 8000 порту

Запросы слать сюда `http://127.0.0.1:8000`
Например, POST на `http://127.0.0.1:8000/generate`

Тело запроса, например
```
{
    "passphrase": "aaa",
    "secret": "ku-ku"
}
```

Запустить только тесты можно командой `docker-compose run tests`


__Настройки окружения__

Сервис имеет следующие настройки через переменные окружения

- MONGO_URI - например, mongodb://localhost:27017/

- MONGO_DATABASE - имя БД в котором будут храниться данные сервиса, например, default или secrets

- RATE_LIMIT_PER_MINUTE - целое число, отвечающее за максимальное число запросов на один URL в минуту

Указать при запуске переменные для самого сервиса можно, например, так

`RATE_LIMIT_PER_MINUTE=1 docker-compose up`

Для только тестов вот так

`docker-compose run -e RATE_LIMIT_PER_MINUTE=1 tests`
