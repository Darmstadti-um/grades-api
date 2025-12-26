# Инструкция по загрузке на GitHub

## Быстрый способ (SSH - рекомендуется)

Если у вас SSH ключ добавлен в GitHub (проверено: ✅ ваш ключ работает):

```bash
./deploy_to_github.sh
```

Скрипт предложит выбрать SSH или HTTPS. Выберите SSH (вариант 1) и введите:
- Имя пользователя GitHub
- Название репозитория

## С использованием токена GitHub (HTTPS)

Если у вас есть Personal Access Token:

```bash
GITHUB_TOKEN=your_token_here GITHUB_REPO_URL=https://github.com/username/grades-api.git ./deploy_to_github.sh
```

## Создание токена GitHub

1. Перейдите в Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Нажмите "Generate new token"
3. Выберите права: `repo` (полный доступ к репозиториям)
4. Скопируйте токен и используйте в команде выше

## Переменные окружения

- `GITHUB_TOKEN` - токен для авторизации
- `GITHUB_REPO_URL` - URL репозитория
- `GITHUB_BRANCH` - ветка (по умолчанию: main)
- `COMMIT_MESSAGE` - сообщение коммита
- `GIT_USER_NAME` - имя для git config
- `GIT_USER_EMAIL` - email для git config
- `FORCE_COMMIT` - принудительный коммит даже если нет изменений

## Примеры использования

### SSH (рекомендуется, если ключ добавлен в GitHub)

```bash
./deploy_to_github.sh
# Выберите вариант 1 (SSH)
# Введите: username и название репозитория
```

Или напрямую:

```bash
GITHUB_REPO_URL=git@github.com:username/grades-api.git ./deploy_to_github.sh
```

### HTTPS с токеном

```bash
GITHUB_TOKEN=ghp_xxxxxxxxxxxx \
GITHUB_REPO_URL=https://github.com/username/grades-api.git \
GITHUB_BRANCH=main \
COMMIT_MESSAGE="Initial commit" \
./deploy_to_github.sh
```

## Проверка SSH подключения

Ваш SSH ключ уже настроен и работает! Проверить можно командой:

```bash
ssh -T git@github.com
```

Должно вывести: "Hi [username]! You've successfully authenticated..."

