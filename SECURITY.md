# SECURITY.md

Документ описывает реальные меры безопасности, реализованные в проекте **QazEdu Special**, и указывает, в каких файлах они находятся. Здесь нет гипотетических или несуществующих механизмов — только то, что есть в текущем коде.

## 1. Security Overview

В проекте реализованы следующие основные механизмы безопасности:

- **JWT‑аутентификация** с проверкой токена и защитой большинства API‑эндпоинтов.
- **Безопасное хранение паролей** с использованием `bcrypt` и усечением пароля до лимита библиотеки.
- **Разделение ролей** (`student`, `teacher`, `admin`) и проверка прав доступа на backend.
- **Admin‑only‑роуты** и проверки учителя/админа для управленческих операций.
- **Защищённый AI‑эндпоинт** (доступен только аутентифицированным пользователям, зависит от наличия `GEMINI_API_KEY`).
- **Валидация входных данных** через Pydantic/SQLModel‑схемы.
- **Использование переменных окружения** для `SECRET_KEY`, `DATABASE_URL`, `GEMINI_API_KEY` и admin‑учётки.
- **Игнорирование `.env` в Git** и наличие безопасного шаблона `backend/.env.example`.
- **Минимальные ограничения на уровне базы**: уникальный email пользователя, связи между сущностями через внешние ключи (через модели SQLModel и миграции Alembic).

Ниже детали по каждому аспекту.

## 2. Authentication (JWT)

**Файлы:**

- `backend/app/api/auth.py`
- `backend/app/api/deps.py`
- `backend/app/core/security.py`
- `backend/app/core/config.py`

**Реализация:**

- JWT‑токен создаётся функцией `create_access_token` в `backend/app/core/security.py`.  
  - Используется библиотека `python-jose` (`jwt.encode`).  
  - Поля токена: `sub` (ID пользователя) и `exp` (время истечения).  
  - Подпись выполняется с использованием `settings.secret_key` и алгоритма `settings.algorithm`.
- В `backend/app/api/auth.py`:
  - Endpoint `POST /api/auth/login` принимает `email` и `password`, ищет пользователя в БД и вызывает `verify_password`.  
  - При успешной проверке возвращает объект `TokenResponse` с `access_token` и данными пользователя.
- В `backend/app/api/deps.py`:
  - Определён HTTP Bearer‑security (`security = HTTPBearer(auto_error=False)`).  
  - Функция `get_current_user` читает заголовок `Authorization`, извлекает токен и декодирует его через `decode_access_token` (`backend/app/core/security.py`).  
  - При отсутствии/ошибке токена выбрасываются корректные HTTP‑ошибки 401 с заголовком `WWW-Authenticate: Bearer`.  
  - `CurrentUser` — alias для зависимости, которая автоматически подставляет текущего пользователя во все защищённые роуты.

**Вывод:** JWT‑аутентификация реализована централизованно, большинство бизнес‑роутов требуют `CurrentUser` (значит, защищены JWT‑токеном).

## 3. Password Security

**Файлы:**

- `backend/app/core/security.py`
- `backend/app/models/user.py`
- `backend/app/api/auth.py`
- `backend/app/api/users.py` (смена пароля через `/api/me/password` — в схемах/роутах)

**Реализация:**

- В `backend/app/models/user.py`:
  - Поле `password_hash` хранит только хэш (нет хранения пароля в открытом виде).  
  - Пароли не возвращаются в ответах API (см. `UserResponse` и функции `user_to_response` в `auth.py`/`users.py`).
- В `backend/app/core/security.py`:
  - Пароли хэшируются с использованием `bcrypt` (`hash_password` и `verify_password`).  
  - Введён лимит `MAX_PASSWORD_BYTES = 72` и функция `_truncate_for_bcrypt`, которая усечёт байты пароля до максимума, поддерживаемого `bcrypt`. Это предотвращает неожиданные отрезания внутри самой библиотеки.
- В `backend/app/api/auth.py`:
  - При регистрации пароль сразу хэшируется: `password_hash=hash_password(body.password)`.  
  - При логине используется `verify_password(plain_password, password_hash)`.
- Смена пароля реализована через защищённый endpoint `/api/me/password` (файл `backend/app/api/users.py`): пользователь должен быть аутентифицирован, там выполняется проверка текущего пароля и установка нового хэша (используется тот же `hash_password`).

**Ограничения:**

- Отсутствует сложная проверка надёжности пароля (нет проверки длины/символов/словарных паролей — используется только базовая валидация схемой Pydantic).  

## 4. Authorization and Roles

**Файлы:**

- `backend/app/models/user.py`
- `backend/app/api/deps.py`
- `backend/app/api/admin.py`
- `backend/app/api/courses.py`
- `backend/app/api/lessons.py`
- `backend/app/api/quizzes.py`
- `backend/app/api/progress.py`
- `backend/app/api/news.py`
- `backend/app/api/community.py`
- `backend/app/api/teacher.py`
- `backend/app/api/ai.py`
+ `backend/app/api/enrollments.py`

**Реализация ролей:**

- В `backend/app/models/user.py` поле `role: str = Field(default="student")` с допустимыми значениями `"student"`, `"teacher"`, `"admin"` (см. `Role = Literal["student", "teacher", "admin"]`).
- В `backend/app/api/deps.py` реализованы функции:
  - `require_teacher_or_admin(user: User)` — выбрасывает 403, если роль не `teacher` и не `admin`.  
  - `require_admin(user: User)` — выбрасывает 403, если роль не `admin`.
- Примеры использования:
  - `backend/app/api/admin.py`: все эндпоинты (`/admin/stats`, `/admin/users*`) вызывают `require_admin(current_user)` — строго admin‑only.  
  - `backend/app/api/courses.py`:  
    - создание/редактирование/удаление курса — только teacher (владелец) или admin (`require_teacher_or_admin` + `_can_manage_course`).  
  - `backend/app/api/lessons.py`:  
    - создание/редактирование/удаление уроков — teacher‑владелец курса или admin (`require_teacher_or_admin`, `_can_manage_lesson`).  
  - `backend/app/api/quizzes.py`:  
    - создание/управление квизами, вопросами и ответами — teacher‑владелец соответствующего курса или admin (`require_teacher_or_admin`, `_can_manage_quiz`).  
    - студенты видят только квиз без правильных ответов (используются разные схемы `QuizResponseStudent` и `QuizResponse`).  
    - доступ к квизу/попыткам ограничен только записанными студентами (`_is_enrolled`).  
  - `backend/app/api/news.py`:  
    - чтение опубликованных новостей доступно всем аутентифицированным пользователям.  
    - просмотр неопубликованных и любая модификация (`/news/admin/all`, `POST /news`, `PATCH /news/{id}`, `DELETE /news/{id}`) — только admin (`require_admin`).  
  - `backend/app/api/community.py`:  
    - все действия (создание, лайк, удаление) доступны только аутентифицированным пользователям; удалять пост может автор или admin (проверка `post.user_id != current_user.id and current_user.role != "admin"`).  
  - `backend/app/api/teacher.py`:  
    - teacher‑статистика и список студентов строятся на основе `CurrentUser`, логика завязана на роли `teacher` (файл проверяет роль текущего пользователя).  
  - `backend/app/api/ai.py`:  
    - AI‑чат доступен только аутентифицированным пользователям (зависимость `CurrentUser`).

**Отдельная защита регистрации admin:**

- В `backend/app/api/auth.py` endpoint `/auth/register`:
  - Если `body.role == "admin"`, выбрасывается 403: `"Admin accounts cannot be created through registration"`.  
  - Это предотвращает создание администраторов через публичный endpoint.

## 5. Protected API Endpoints (обзор)

Практически все бизнес‑маршруты используют зависимость `CurrentUser` (см. `backend/app/api/deps.py`) и, следовательно, требуют валидного JWT‑токена:

- **Профиль / личный кабинет:** `backend/app/api/users.py`, `backend/app/api/auth.py`  
  - `/api/me`, `/api/me` (PATCH), `/api/me/password`, `/api/me/achievements`, `/api/me/study-friends` — все требуют `CurrentUser`.
- **Курсы и уроки:** `backend/app/api/courses.py`, `backend/app/api/lessons.py`, `backend/app/api/enrollments.py`  
  - Просмотр курсов и уроков — только аутентифицированные пользователи.  
  - Создание/изменение/удаление курсов и уроков — только teacher‑владелец или admin.
- **Квизы и прогресс:** `backend/app/api/quizzes.py`, `backend/app/api/progress.py`  
  - Создание и управление квизами — только teacher/admin.  
  - Доступ к квизам и отправка ответов — только записанные студенты/учителя/админы (через `_is_enrolled`).  
  - Прогресс уроков и курсов всегда завязан на текущего пользователя (`CurrentUser`).
- **Админ‑раздел:** `backend/app/api/admin.py`  
  - Все роуты (`/api/admin/*`) доступны только admin через `require_admin`.
- **Учительский раздел:** `backend/app/api/teacher.py`  
  - Доступ защищён, используется текущий пользователь и его роль `teacher` для выборки данных.
- **Сообщество:** `backend/app/api/community.py`  
  - Любые операции (создание постов, лайки, удаление) доступны только аутентифицированным пользователям.  
  - Удаление ограничено автором поста или admin.
- **Новости:** `backend/app/api/news.py`  
  - Все операции требуют аутентификации (даже чтение новостей использует `CurrentUser`).  
  - Управление новостями — только admin.
- **AI‑чат:** `backend/app/api/ai.py`  
  - Доступен только аутентифицированным пользователям. При отсутствии `GEMINI_API_KEY` отрабатывает 503.

## 6. Input Validation

**Файлы:**

- `backend/app/schemas/*.py`
- `backend/app/models/*.py`
- `backend/app/api/*.py`

**Реализация:**

- Все входные данные в бизнес‑роутах типизированы через Pydantic‑схемы (`UserCreate`, `UserLogin`, `CourseCreate`, `LessonCreate`, `QuizCreate`, `NewsCreate`, `SuccessPostCreate`, и т.д.).  
  - Например, в `backend/app/api/auth.py` тело запроса `register` — это `UserCreate`, в `news.py` — `NewsCreate`/`NewsUpdate`, в `quizzes.py` — `QuizCreate`, `QuestionCreate`, `AnswerCreate` и пр.
- SQLModel‑модели определяют типы и некоторые ограничения поля (например, `email` уникален и индексирован, `is_published` — bool, `role` — строка с допустимыми значениями).
- Во многих местах есть дополнительная ручная валидация:
  - Проверка уникальности email при регистрации (`auth.py`, `select(User).where(User.email == body.email)`).  
  - Проверка, что контент поста сообщества не пустой (`community.py`, `if not body.content.strip(): ...`).  
  - Проверка, что квиз для урока не создаётся повторно (`quizzes.py`, `Quiz` по `lesson_id`).  
  - Проверка корректности ID‑ответов и принадлежности их к вопросу/квизу при проверке ответа и отправке квиза.

**Ограничения:**

- Нет строгой централизованной проверки сложности паролей.  
- Часть бизнес‑ограничений реализована вручную в коде (без декларативных `CheckConstraint`), но они присутствуют (например, запрет дублирования квиза для урока, запрет пустого контента).

## 7. Environment and Secrets

**Файлы:**

- `backend/app/core/config.py`
- `backend/.env.example`
- `.gitignore`

**Реализация:**

- Конфигурация загружается через `pydantic-settings` в `backend/app/core/config.py`:
  - `database_url` (по умолчанию SQLite, можно переопределить через `DATABASE_URL`).  
  - `secret_key` — **обязательная** переменная (тип `str` без дефолта).  
  - `algorithm` и `access_token_expire_minutes`.  
  - `cors_origins` — строка со списком разрешённых origin через запятую.  
  - `gemini_api_key` — по умолчанию пустая строка.  
  - `admin_email`, `admin_password`, `admin_first_name`, `admin_last_name` — все `Optional`, используются только для seed‑логики.
- В `backend/.env.example`:
  - Приведён безопасный шаблон с явным комментарием, что `SECRET_KEY` нужно сгенерировать и заменить.  
  - Есть комментарии, что admin‑аккаунт создаётся только при заполненных `ADMIN_*`.  
  - `GEMINI_API_KEY` указан как опциональный ключ для AI‑функциональности.
- В `.gitignore`:
  - `.env` и все производные файлы окружения игнорируются (`.env`, `.env.*`, `.env.local` и т.д.).  
  - `.env.example` явно **не** игнорируется, используется как публичный шаблон.
- Использование `SECRET_KEY`:
  - В `backend/app/core/security.py` токен шифруется и расшифровывается с использованием `settings.secret_key`.  
  - При отсутствии `SECRET_KEY` приложение не стартует (так как поле обязательно для `Settings`).  

**GEMINI_API_KEY и AI:**

- Ключ AI берётся только из `settings.gemini_api_key`.  
- В `backend/app/api/ai.py` при пустом ключе возвращается 503 с понятным сообщением (`"AI service is not configured"`).  
- На frontend ключ не передаётся и не хранится, используется только на backend.

## 8. Database and Migration Safety

**Файлы:**

- `backend/app/models/*.py`
- `backend/alembic/versions/*.py`

**Реализация:**

- Модели SQLModel определяют:
  - `User` — уникальный email (`Field(unique=True, index=True)`), роль, временные метки.  
  - `Enrollment`, `LessonProgress`, `Quiz`, `Question`, `Answer`, `QuizAttempt`, `News`, `SuccessPost`, `SuccessPostLike` и др. — явные связи через `foreign_key` строки.  
  - Многие поля обязательные (без `default=None`), что минимизирует количество `NULL` там, где они не нужны.
- Alembic миграции (`backend/alembic/versions/*.py`) поддерживают структуру таблиц для PostgreSQL, в том числе:
  - Добавление новых полей (`image_url` для `courses`, `media_url`/`media_type` для `news`).  
  - Первичные ключи, внешние ключи и типы данных.
- Для SQLite:
  - При старте приложения, если `DATABASE_URL` содержит `sqlite`, вызывается `create_db_and_tables()` (`backend/app/db/session.py`, `backend/app/main.py`), который создаёт таблицы по **текущим** моделям (без Alembic).  
  - Это удобно для локальной разработки, но структура может немного отличаться от продакшн‑PostgreSQL, если миграции ушли вперёд.

**Ограничения:**

- Не все бизнес‑ограничения реализованы на уровне БД (например, запрет двойной записи на курс может быть реализован логикой, а не уникальным индексом student‑course).  
- Нет явного механизма “soft delete”, все удаления — физические.

## 9. CORS and API Access

**Файлы:**

- `backend/app/main.py`
- `backend/app/core/config.py`

**Реализация:**

- В `backend/app/main.py`:
  - Добавляется `CORSMiddleware` из FastAPI:  
    - `allow_origins=settings.cors_origins.split(",")`  
    - `allow_credentials=True`, `allow_methods=["*"]`, `allow_headers=["*"]`.
- В `backend/app/core/config.py`:
  - `cors_origins` задаётся строкой, по умолчанию `http://localhost:5173,http://localhost:3000`.  
  - В `.env` можно изменить список origin без правки кода.

**Ограничения:**

- CORS разрешает любые методы и заголовки; ограничения по методам не настраиваются отдельно.  
- CORS — это не механизм аутентификации, а только настройка доступа из браузера; он корректно используется, но не заменяет защиту JWT.

## 10. Frontend Security Aspects

**Файлы:**

- `frontend/src/api/client.ts`
- `frontend/src/contexts/AuthContext.tsx`
- Компоненты, проверяющие роль (например, дашборд, админ‑панель, teacher‑страницы)

**Реализация:**

- **Хранение токена:**
  - В `AuthContext.tsx` используется `localStorage` для хранения `token` и `user` (`TOKEN_KEY = 'token'`, `USER_KEY = 'user'`).  
  - Это стандартный подход для SPA, но он уязвим к XSS (см. ограничения ниже).
- **Отправка токена:**
  - В `frontend/src/api/client.ts` функция `getAuthHeader` читает токен из `localStorage` и добавляет `Authorization: Bearer <token>` ко всем запросам (`apiRequest`).  
  - Все API‑клиенты фронта строятся на `apiRequest`, поэтому заголовок отправляется централизованно.
- **Обработка 401/ошибок:**
  - `apiRequest` бросает ошибку, если `res.ok` `false`, извлекая `detail` из ответа; это используемая модель на уровне UI.  
  - В `AuthContext.tsx` при неуспешном `getMe()` токен сбрасывается (`persist(null, null)`), что по сути выполняет “форс‑лог‑аут” при истекшем/некорректном токене.
- **Ролевая защита UI:**
  - Контекст `AuthContext` предоставляет `userRole` и `isAuthenticated`.  
  - Компоненты (например, админ‑панель, teacher‑страницы) проверяют роль и не отображают функционал, если роль не подходит. Это добавляет **UI‑уровень** защиты, но основная безопасность обеспечивается backend‑проверками.
- **Отсутствие хардкода секретов:**
  - На фронтенде нет прямого хранения `SECRET_KEY` или `GEMINI_API_KEY`.  
  - Конфигурация API‑урла берётся из `import.meta.env.VITE_API_URL` или через Vite‑proxy.

**Ограничения:**

- Используется `localStorage` (нет HTTP‑only cookies), что потенциально уязвимо при наличии XSS. В коде нет дополнительного слоя защиты от XSS (например, строгих CSP, санитайзеров HTML).

## 11. Existing Security Limitations

В текущей реализации **отсутствуют** следующие механизмы (или они не обнаружены в коде):

- **Rate limiting / защита от brute‑force** на уровне login‑эндпоинта (`/api/auth/login` не ограничивает количество попыток).  
- **Refresh tokens** и отдельное обновление access‑токенов. Используется только один JWT без механизма обновления.  
- **Защита от CSRF** как отдельный слой (используется Bearer‑токен, но нет CSRF‑токенов/заголовков).  
- **HTTP‑only secure cookies** для токена — применяется `localStorage`.  
- **Расширенный аудит и логирование безопасности** (логин/логаут/смена пароля/админ‑действия не логируются отдельно).  
- **Детальный контроль сложностей пароля** (проверка длины/символов/черного списка).  
- **WAF, IDS/IPS, интеграция с SIEM** или подобные enterprise‑механизмы.  
- **Защита от массовых запросов к AI‑эндпоинту** (нет специфического rate‑limit на `/api/ai/chat`).  

Все эти моменты **честно отсутствуют в коде** и не заявляются как реализованные.

## 12. Краткое резюме

- **Найденные механизмы безопасности:**
  - JWT‑аутентификация (`backend/app/core/security.py`, `backend/app/api/auth.py`, `backend/app/api/deps.py`).  
  - Безопасное хранение паролей через `bcrypt` и усечение до 72 байт (`security.py`, `user.py`).  
  - Ролевое разграничение доступа и admin‑only‑роуты (`deps.py`, `admin.py`, `courses.py`, `lessons.py`, `quizzes.py`, `news.py`, `community.py`, `teacher.py`).  
  - Запрет регистрации admin через публичный endpoint (`auth.py`).  
  - Валидация данных через Pydantic/SQLModel‑схемы (`schemas/*.py`, большинство роутов в `api/*.py`).  
  - Использование `.env` и шаблона `.env.example` с обязательным `SECRET_KEY` и опциональным `GEMINI_API_KEY` (`config.py`, `.env.example`, `.gitignore`).  
  - Настройка CORS через `CORSMiddleware` (`main.py`, `config.py`).  
  - Защищённый AI‑эндпоинт, зависящий от `GEMINI_API_KEY` (`ai.py`).  
  - Уникальность email и базовые связи между сущностями в моделях и миграциях.

- **Основные файлы, где реализованы меры безопасности:**
  - Backend: `backend/app/core/security.py`, `backend/app/core/config.py`, `backend/app/api/deps.py`, `backend/app/api/auth.py`, `backend/app/api/admin.py`, `backend/app/api/courses.py`, `backend/app/api/lessons.py`, `backend/app/api/quizzes.py`, `backend/app/api/progress.py`, `backend/app/api/news.py`, `backend/app/api/community.py`, `backend/app/api/teacher.py`, `backend/app/api/ai.py`, `backend/app/models/*.py`, `backend/alembic/versions/*.py`.  
  - Frontend: `frontend/src/api/client.ts`, `frontend/src/contexts/AuthContext.tsx`, компоненты с ролевым рендерингом.

- **Честно отмеченные ограничения:**
  - Нет rate limiting и защиты от brute‑force.  
  - Нет refresh‑токенов, CSRF‑слоя и HTTP‑only cookies.  
  - Нет расширенной проверки сложности паролей и аудита безопасности.  
  - Использование `localStorage` для токена на фронте уязвимо к XSS, при этом отдельного XSS‑слоя в коде нет.  

Этот документ отражает **фактическое состояние** безопасности в текущей версии проекта, без добавления несуществующих механизмов.

