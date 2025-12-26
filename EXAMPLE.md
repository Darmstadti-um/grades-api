# Примеры использования API

## Загрузка CSV файла

```bash
curl -X POST "http://localhost:8000/upload-grades" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@students_grades.csv"
```

## Получение студентов с более чем 3 двойками

```bash
curl -X GET "http://localhost:8000/students/more-than-3-twos" \
  -H "accept: application/json"
```

## Получение студентов с менее чем 5 двойками

```bash
curl -X GET "http://localhost:8000/students/less-than-5-twos" \
  -H "accept: application/json"
```

## Проверка здоровья сервиса

```bash
curl -X GET "http://localhost:8000/health"
```

## Пример CSV файла

```csv
Дата;Номер группы;ФИО;Оценка
11.03.2025;101Б;Иванов Иван Иванович;4
18.09.2024;102Б;Петров Пётр Петрович;2
26.09.2024;103М;Сидоров Сидор Сидорович;5
```

