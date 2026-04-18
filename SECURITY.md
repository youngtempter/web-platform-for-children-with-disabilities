# SECURITY.md

Документ описывает реальные меры безопасности в проекте **QazEdu Special**. Только фактически реализованные механизмы.

## 1. Аутентификация

### JWT

- Токен создаётся в `backend/app/core/security.py` через `python-jose`.
- Поля: `sub` (ID пользователя), `exp` (срок истечения).
- Подписывается `SECRET_KEY` (алгоритм HS256).
- `get_current_user` в `backend/app/api/deps.py` декодирует токен при каждом запросе.
- При невалидном токене — 401 с заголовком `WWW-Authenticate: Bearer`.

### Email верификация

- При регистрации генерируется `verification_token` (UUID), сохраняется в БД с TTL 24 часа.
- Письмо отправляется через `aiosmtplib` (`backend/app/core/email.py`).
- Логин невозможен без подтверждения email (`is_verified=False` → 403).
- Эндпоинт `/api/auth/resend-verification` с rate limit 3/мин.

### Google OAuth

- Реализован через `authlib` + `SessionMiddleware` (itsdangerous).
- Флоу: `/api/auth/google` → Google → `/api/auth/google/callback`.
- При первом входе создаётся аккаунт с `is_verified=True`, при повторном — выдаётся токен.
- Redirect URI должен быть зарегистрирован в Google Cloud Console.

### Сброс пароля

- `/api/auth/forgot-password` генерирует `reset_token` (UUID) с TTL 1 час, отправляет письмо.
- `/api/auth/reset-password` проверяет токен, устанавливает новый хэш пароля.
- После использования токен обнуляется.

## 2. Безопасность паролей

- Хранится только `password_hash` (bcrypt), пароль никогда не возвращается в ответах API.
- `hash_password` / `verify_password` в `backend/app/core/security.py`.
- Усечение до 72 байт (`MAX_PASSWORD_BYTES`) для корректной работы bcrypt.
- Google OAuth пользователи не имеют пароля (`password_hash=None`).

## 3. Rate Limiting (slowapi)

Реализован через `slowapi` в `backend/app/core/limiter.py`, применяется в `backend/app/api/auth.py`:

| Endpoint | Лимит |
|----------|-------|
| `POST /api/auth/register` | 5 запросов/мин |
| `POST /api/auth/login` | 10 запросов/мин |
| `POST /api/auth/resend-verification` | 3 запроса/мин |
| `POST /api/auth/forgot-password` | 3 запроса/мин |

При превышении — 429 Too Many Requests.

## 4. Security Headers (XSS защита)

`SecurityHeadersMiddleware` в `backend/app/main.py` добавляет заголовки ко всем ответам:

| Заголовок | Значение |
|-----------|----------|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `X-XSS-Protection` | `1; mode=block` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Content-Security-Policy` | ограничивает источники скриптов, стилей, фреймов |

CSP разрешает: `'self'`, `'unsafe-inline'`, `'unsafe-eval'`, `cdn.jsdelivr.net` (для Swagger UI), YouTube фреймы.

## 5. Роли и авторизация

Три роли: `student`, `teacher`, `admin` (поле `role` в модели `User`).

Функции в `backend/app/api/deps.py`:
- `require_teacher_or_admin` — 403 если не teacher/admin
- `require_admin` — 403 если не admin

| Роут | Защита |
|------|--------|
| `POST /api/auth/register` с `role=admin` | 403 запрещено |
| `/api/admin/*` | только admin |
| Создание/редактирование курсов, уроков, квизов | только teacher-владелец или admin |
| Удаление поста сообщества | автор или admin |
| Управление новостями | только admin |
| `/api/ai/chat` | любой аутентифицированный |

## 6. CORS

`CORSMiddleware` в `backend/app/main.py`:
- `allow_origins` — из `CORS_ORIGINS` в `.env` (через запятую)
- `allow_credentials=True`, `allow_methods=["*"]`, `allow_headers=["*"]`

В продакшене `CORS_ORIGINS` должен содержать только домен фронтенда.

## 7. Валидация входных данных

- Все входные данные типизированы через Pydantic-схемы (`backend/app/schemas/*.py`).
- Уникальность email проверяется при регистрации.
- Запрет пустого контента в постах сообщества.
- Запрет повторного создания квиза для урока.
- Проверка принадлежности ответов к вопросу при сдаче квиза.

## 8. Переменные окружения и секреты

- Все секреты загружаются через `pydantic-settings` из `.env`.
- `.env` и все `*.env.*` файлы в `.gitignore`.
- `SECRET_KEY` обязателен — без него приложение не стартует.
- При пустом `GEMINI_API_KEY` — `/api/ai/chat` возвращает 503.
- На фронтенде нет секретов — только `VITE_API_URL`.

## 9. Фронтенд

- Токен хранится в `localStorage` (стандарт для SPA).
- `Authorization: Bearer <token>` добавляется централизованно в `frontend/src/api/client.ts`.
- При 401 — токен сбрасывается, пользователь разлогинивается.
- Ролевая защита UI (admin/teacher страницы) — дополнительный слой, основная защита на backend.
- Google OAuth callback обрабатывается через URL параметры (`?auth_token=`, `?auth_error=`).

## 10. Ограничения

- Нет refresh-токенов — только один JWT без механизма обновления.
- `localStorage` для токена уязвим к XSS (нет HTTP-only cookies).
- Нет CSRF-токенов (Bearer-токен частично защищает, но не полностью).
- Нет проверки сложности пароля (длина, символы, словарные пароли).
- Нет аудита безопасности (логин/логаут/смена пароля не логируются отдельно).
- Нет rate limit на `/api/ai/chat`.
- Нет soft delete — все удаления физические.
