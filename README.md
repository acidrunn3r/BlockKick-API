# BlockKick-API
**REST API для платформы BlockKick**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)

Связанные репозитории:
- [BlockKick](https://github.com/andre1vorobei/BlockKick)
- [BlockKick-CLI](https://github.com/acidrunn3r/BlockKick-CLI)

## Установка

### Требования
- Python 3.11 или выше
- [Docker](https://www.docker.com/) и Docker Compose

### Шаг 1: Склонируйте репозиторий

```bash
git clone https://github.com/acidrunn3r/BlockKick-API.git
cd BlockKick-API
```


### Шаг 2: Создайте файл окружения

```bash
cp .env.example .env
```


### Шаг 3: Запустите сервисы

```bash
make up
```


### Шаг 4: Примените миграции

```bash
make migrate
```


#### API будет доступен по адресу `http://localhost:8000`

## Разработка

### Требования
- Python 3.11 или выше
- [Poetry](https://python-poetry.org/)

### Шаг 1: Установите зависимости

```bash
poetry install --with dev
```


### Шаг 2: Запустите тесты

```bash
make test
```


#### Линтинг и форматирование

```bash
make lint    # проверка
make format  # автоисправление
```


## Эндпоинты

### `GET /health`
Проверка состояния сервиса.

### `GET /api/v1/chain/info`
Текущее состояние блокчейна: высота цепи и хэш последнего блока.

### `GET /api/v1/wallets/{address}/transactions`
История транзакций кошелька из индексированной БД (отправитель или получатель).
- `address` — публичный ключ кошелька (64 hex-символа)

### `GET /api/v1/projects`
Список краудфандинговых проектов на BlockKick.

### `GET /api/v1/projects/{project_id}`
Детальная информация о проекте: цель, собрано, последние донаторы.

### `POST /api/v1/auth/register`
Зарегистрировать кошелёк через криптографический challenge-response (Ed25519).

### `POST /api/v1/auth/login`
Войти и получить JWT-токен.

### `POST /api/v1/auth/refresh`
Обновить JWT-токен.

### `GET /api/v1/users/me`
Показать профиль текущего пользователя.

### `PUT /api/v1/users/me`
Обновить имя и bio профиля.
