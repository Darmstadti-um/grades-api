#!/bin/bash

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 Подготовка к загрузке на GitHub...${NC}"

# Проверка наличия git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git не установлен${NC}"
    exit 1
fi

# Проверка наличия всех необходимых файлов
echo -e "${YELLOW}📋 Проверка структуры проекта...${NC}"
required_files=(
    "app/main.py"
    "app/db.py"
    "app/schemas.py"
    "app/validators.py"
    "app/settings.py"
    "sql/001_create_tables.sql"
    "docker-compose.yml"
    "Dockerfile"
    "requirements.txt"
    "README.md"
    "tests/test_api.py"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    echo -e "${RED}❌ Отсутствуют файлы:${NC}"
    printf '%s\n' "${missing_files[@]}"
    exit 1
fi

echo -e "${GREEN}✅ Все необходимые файлы на месте${NC}"

# Инициализация git репозитория если его нет
if [ ! -d .git ]; then
    echo -e "${YELLOW}📦 Инициализация git репозитория...${NC}"
    git init
    git config user.name "${GIT_USER_NAME:-GitHub User}" || true
    git config user.email "${GIT_USER_EMAIL:-user@example.com}" || true
fi

# Настройка remote
if ! git remote get-url origin &> /dev/null; then
    if [ -z "$GITHUB_REPO_URL" ]; then
        read -p "Введите URL GitHub репозитория (например: https://github.com/username/grades-api.git): " REPO_URL
        GITHUB_REPO_URL="$REPO_URL"
    fi
    
    # Если используется токен, заменяем URL
    if [ -n "$GITHUB_TOKEN" ]; then
        REPO_NAME=$(echo "$GITHUB_REPO_URL" | sed 's|https://github.com/||' | sed 's|.git||')
        GITHUB_REPO_URL="https://${GITHUB_TOKEN}@github.com/${REPO_NAME}.git"
    fi
    
    echo -e "${YELLOW}📝 Настройка remote репозитория...${NC}"
    git remote add origin "$GITHUB_REPO_URL" || git remote set-url origin "$GITHUB_REPO_URL"
else
    if [ -n "$GITHUB_TOKEN" ]; then
        CURRENT_URL=$(git remote get-url origin)
        REPO_NAME=$(echo "$CURRENT_URL" | sed 's|https://github.com/||' | sed 's|.git||' | sed 's|.*@github.com/||')
        NEW_URL="https://${GITHUB_TOKEN}@github.com/${REPO_NAME}.git"
        git remote set-url origin "$NEW_URL"
    fi
fi

# Добавление всех файлов
echo -e "${YELLOW}📁 Добавление файлов...${NC}"
git add .

# Проверка изменений
if git diff --staged --quiet && [ -z "$FORCE_COMMIT" ]; then
    echo -e "${YELLOW}ℹ️  Нет изменений для коммита${NC}"
    read -p "Продолжить с пушем? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
else
    # Коммит
    echo -e "${YELLOW}💾 Создание коммита...${NC}"
    COMMIT_MSG="${COMMIT_MESSAGE:-Initial commit: FastAPI grades API with PostgreSQL}"
    
    if git diff --staged --quiet; then
        echo -e "${YELLOW}Создание пустого коммита...${NC}"
        git commit --allow-empty -m "$COMMIT_MSG"
    else
        git commit -m "$COMMIT_MSG" || git commit -m "Update: grades API improvements"
    fi
fi

# Пуш в GitHub
echo -e "${YELLOW}⬆️  Загрузка на GitHub...${NC}"
BRANCH="${GITHUB_BRANCH:-main}"

# Проверка существования ветки
if git show-ref --verify --quiet refs/heads/"$BRANCH"; then
    CURRENT_BRANCH=$(git branch --show-current)
    if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
        git checkout -b "$BRANCH" 2>/dev/null || git checkout "$BRANCH"
    fi
else
    git checkout -b "$BRANCH" 2>/dev/null || true
fi

# Пуш
if git push -u origin "$BRANCH" 2>/dev/null; then
    echo -e "${GREEN}✅ Успешно загружено на GitHub!${NC}"
elif git push origin "$BRANCH" 2>/dev/null; then
    echo -e "${GREEN}✅ Успешно загружено на GitHub!${NC}"
else
    echo -e "${RED}❌ Ошибка при загрузке. Проверьте права доступа и токен.${NC}"
    echo -e "${YELLOW}💡 Попробуйте запустить с переменными окружения:${NC}"
    echo "   GITHUB_TOKEN=your_token GITHUB_REPO_URL=https://github.com/user/repo.git ./deploy_to_github.sh"
    exit 1
fi

REPO_URL=$(git remote get-url origin | sed 's|https://.*@github.com/|https://github.com/|' | sed 's|.git||')
echo -e "${GREEN}🔗 Репозиторий: ${REPO_URL}${NC}"
