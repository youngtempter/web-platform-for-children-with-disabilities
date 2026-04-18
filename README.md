# QazEdu Special

**Сайт:** https://web-platform-for-children-with-disabilities-13auzqlf4.vercel.app

Инклюзивная образовательная платформа для глухих и слабослышащих детей с поддержкой видеоуроков, субтитров и жестового языка.

## О проекте

QazEdu Special — веб‑платформа дистанционного обучения для детей с нарушениями слуха.  
Система предоставляет структурированные курсы и уроки, интерактивные квизы, отслеживание прогресса, новости платформы, сообщество успехов и AI‑помощника для поддержки обучения.

### Основные возможности

- **Курсы и уроки**: структурированные учебные материалы с видео, текстом, субтитрами и жестовым сопровождением.
- **Интерактивные квизы**: тесты с автопроверкой, подсчётом баллов и сохранением попыток.
- **Прогресс**: отслеживание прохождения уроков и курсов.
- **Сообщество**: "стена успехов" с лайками и список учебных друзей.
- **Новости**: лента с медиаконтентом (YouTube/изображения).
- **AI‑помощник**: интеграция с Google Gemini.
- **Аутентификация**: email‑верификация, Google OAuth, сброс пароля по email.
- **Роли**: student, teacher, admin.
- **Двуязычный интерфейс**: русский и казахский.
- **Светлая/тёмная тема**.

## Технологии

| Компонент | Стек |
|-----------|------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui |
| Backend | FastAPI, SQLModel, PostgreSQL (Neon), Alembic |
| Аутентификация | JWT, bcrypt, email‑верификация (aiosmtplib), Google OAuth (authlib) |
| Безопасность | slowapi (rate limiting), CSP/XSS headers, SessionMiddleware |
| AI | Google Gemini API |
| Деплой | Railway (backend), Vercel (frontend) |
| Docker | docker-compose для локального запуска |

## Структура проекта

```text
web-platform-for-children-with-disabilities/
├── docker-compose.yml             # Локальный запуск (backend + frontend)
├── frontend/
│   ├── Dockerfile                 # Multi-stage: node builder + nginx
│   ├── nginx.conf                 # SPA routing + /api proxy на backend
│   ├── vercel.json                # Vercel SPA rewrites
│   └── src/
│       ├── api/                   # API‑клиенты
│       ├── components/            # Страницы и UI‑блоки
│       ├── components/ui/         # shadcn/ui компоненты
│       └── contexts/              # Auth, язык, тема
└── backend/
    ├── Dockerfile
    ├── requirements.txt
    └── app/
        ├── api/                   # Роуты: auth, users, courses, lessons, enrollments, quizzes, progress, admin, teacher, news, community, ai
        ├── models/                # SQLModel модели
        ├── schemas/               # Pydantic схемы
        ├── core/                  # config, security, email, limiter, seed
        ├── db/                    # engine, session
        └── main.py                # FastAPI app, middleware, роуты
```

## Запуск с Docker (рекомендуется)

```bash
# Клонировать репо
git clone https://github.com/kaldybekoff/web-platform-for-children-with-disabilities.git
cd web-platform-for-children-with-disabilities

# Создать backend/.env (см. раздел ниже)

# Запустить
docker-compose up --build
```

- Фронтенд: http://localhost:3000  
- Бэкенд API: http://localhost:8000  
- Swagger UI: http://localhost:8000/docs

При изменении кода пересобрать: `docker-compose up --build`  
Остановить: `docker-compose down`

## Запуск вручную

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows
# source .venv/bin/activate       # macOS/Linux
pip install -r requirements.txt
alembic upgrade head
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173 (Vite проксирует `/api` на backend)

## Переменные окружения (backend/.env)

Создай `backend/.env` на основе `backend/.env.example`:

```env
# База данных
DATABASE_URL=postgresql://user:password@host:5432/dbname

# JWT
SECRET_KEY=your-secure-secret-key   # python -c "import secrets; print(secrets.token_urlsafe(32))"
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Админ (автосоздание при старте)
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=StrongPassword123!
ADMIN_FIRST_NAME=System
ADMIN_LAST_NAME=Admin

# AI (опционально)
GEMINI_API_KEY=your-gemini-api-key

# Email верификация (Gmail App Password)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
SMTP_FROM_EMAIL=your@gmail.com
SMTP_FROM_NAME=QazEdu Special
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-secret
```

## Деплой

### Backend → Railway

1. Создай проект на [railway.app](https://railway.app) из GitHub репо
2. Root Directory: `backend`
3. Добавь все переменные из `.env` в Variables
4. Обнови `FRONTEND_URL`, `BACKEND_URL`, `CORS_ORIGINS` на продакшн URL

### Frontend → Vercel

1. Импортируй репо на [vercel.com](https://vercel.com)
2. Root Directory: `frontend`
3. Добавь переменную: `VITE_API_URL=https://your-railway-url.railway.app`

### Google OAuth (продакшн)

В Google Cloud Console → Credentials → OAuth Client добавь Authorized redirect URI:
```
https://your-railway-url.railway.app/api/auth/google/callback
```

## Аутентификация и роли

- **JWT** — Bearer‑токен в `Authorization` заголовке
- **Email верификация** — при регистрации отправляется письмо со ссылкой
- **Google OAuth** — вход через Google аккаунт
- **Forgot Password** — письмо со ссылкой для сброса (TTL 1 час)
- **Rate limiting** — 5/мин регистрация, 10/мин логин, 3/мин resend/forgot

### Роли

| Роль | Возможности |
|------|-------------|
| **student** | Курсы, уроки, квизы, прогресс, сообщество, AI‑чат |
| **teacher** | Создание курсов/уроков/квизов, статистика студентов |
| **admin** | Управление пользователями, курсами, новостями, статистика |

## Основные API endpoints

### Аутентификация

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/api/auth/register` | Регистрация (отправляет письмо верификации) |
| POST | `/api/auth/login` | Вход, выдача JWT |
| GET | `/api/auth/verify` | Подтверждение email по токену из письма |
| POST | `/api/auth/resend-verification` | Повторная отправка письма верификации |
| POST | `/api/auth/forgot-password` | Запрос сброса пароля |
| POST | `/api/auth/reset-password` | Установка нового пароля |
| GET | `/api/auth/google` | Редирект на Google OAuth |
| GET | `/api/auth/google/callback` | Callback Google OAuth |

### Профиль

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/me` | Текущий пользователь |
| PATCH | `/api/me` | Обновление профиля |
| POST | `/api/me/password` | Смена пароля |
| GET | `/api/me/achievements` | Статистика достижений |
| GET | `/api/me/study-friends` | Учебные друзья |

### Курсы и уроки

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/courses` | Список курсов |
| GET/POST/PATCH/DELETE | `/api/courses/{id}` | CRUD курса |
| POST | `/api/courses/{id}/enroll` | Запись на курс |
| GET/POST/PATCH/DELETE | `/api/lessons/{id}` | CRUD уроков |
| POST | `/api/lessons/{id}/complete` | Отметить урок завершённым |

### Квизы, новости, сообщество, AI

| Endpoint | Описание |
|----------|----------|
| `/api/lessons/{id}/quiz` | Квиз урока |
| `/api/quizzes/{id}/submit` | Сдать квиз |
| `/api/news` | Новости |
| `/api/community/posts` | Стена успехов |
| `/api/ai/chat` | AI‑помощник |
| `/api/admin/*` | Админ‑панель |
| `/api/teacher/*` | Учительская статистика |

## База данных

| Таблица | Описание |
|---------|----------|
| `users` | Пользователи (email, bcrypt хэш, роль, is_verified, google_id, reset_token) |
| `courses` | Курсы |
| `lessons` | Уроки с видео и субтитрами |
| `enrollments` | Записи на курсы |
| `lesson_progress` | Прогресс по урокам |
| `quizzes` / `questions` / `answers` | Квизы |
| `quiz_attempts` | Попытки квизов |
| `news` | Новости |
| `success_posts` / `success_post_likes` | Сообщество |

## Миграции

```bash
alembic upgrade head          # Применить все миграции
alembic downgrade base        # Откатить всё
alembic revision --autogenerate -m "описание"   # Новая миграция
```
