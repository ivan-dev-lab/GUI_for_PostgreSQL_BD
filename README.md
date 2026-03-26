# ИС учета покупки посадочного материала

Учебный настольный проект на Python и PostgreSQL для учета закупки посадочного материала под договоры оформления объектов.

Приложение позволяет:

- вести справочник поставщиков;
- вести каталог цветов и посадочного материала;
- оформлять договоры с заказчиками;
- создавать и сопровождать заказы на поставку;
- рассчитывать суммы заказов и итоговую стоимость по договорам с коэффициентом;
- ограничивать доступ по ролям;
- формировать отчеты с экспортом в CSV и XLSX.

## Стек технологий

- Python 3.11+
- PostgreSQL 15+
- Tkinter
- SQLAlchemy 2.x
- psycopg
- python-dotenv
- pytest
- openpyxl

## Структура проекта

```text
planting_material_accounting/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── constants.py
│   ├── db/
│   ├── gui/
│   ├── models/
│   ├── repositories/
│   ├── services/
│   ├── sql/
│   └── utils/
├── tests/
├── .env.example
├── requirements.txt
├── README.md
└── run.py
```

## Установка PostgreSQL

1. Скачайте PostgreSQL 15 или новее с официального сайта: https://www.postgresql.org/download/
2. Во время установки запомните пароль пользователя `postgres`.
3. Убедитесь, что служба PostgreSQL запущена.
4. Проверьте подключение через `psql` или pgAdmin.

Пример проверки:

```powershell
psql -U postgres -h localhost -p 5432
```

## Создание базы данных

Создайте пустую базу данных, например:

```sql
CREATE DATABASE planting_material_accounting;
```

## Настройка `.env`

1. Скопируйте `.env.example` в `.env`.
2. Укажите параметры подключения к вашей локальной базе.

Пример:

```env
APP_TITLE=ИС учета покупки посадочного материала
DB_DRIVER=postgresql+psycopg
DB_HOST=localhost
DB_PORT=5432
DB_NAME=planting_material_accounting
DB_USER=postgres
DB_PASSWORD=postgres
APP_INIT_WITH_SEED=true
```

Если удобнее, можно задать готовую строку подключения:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/planting_material_accounting
```

## Установка зависимостей

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Инициализация базы данных

Создание таблиц, индексов, представлений и seed-данных:

```powershell
python -m app.db.init_db --drop-existing --with-seed
```

Дополнительно в проекте есть SQL-файлы:

- `app/sql/schema.sql` — схема БД;
- `app/sql/indexes.sql` — индексы;
- `app/sql/views.sql` — SQL-представления;
- `app/sql/seed.sql` — SQL-наполнение тестовыми данными.

## Запуск приложения

```powershell
python run.py
```

## Тестовые логины и пароли

| Логин | Пароль | Роль |
|---|---|---|
| `purchase_manager` | `purchase123` | Менеджер по закупкам |
| `sales_manager` | `sales123` | Менеджер по продажам |
| `warehouse_manager` | `warehouse123` | Заведующий складом |
| `analyst` | `analyst123` | Аналитик / Бухгалтер |

## Описание ролей

### Менеджер по закупкам

- `suppliers` — CRUD
- `flowers` — CRUD
- `purchase_orders` — только просмотр
- `contracts` — доступа нет

### Менеджер по продажам

- `contracts` — CRUD
- `purchase_orders` — CRUD
- `suppliers` — только просмотр
- `flowers` — только просмотр

### Заведующий складом

- `flowers` — только просмотр
- `contracts` — только просмотр
- `purchase_orders` — только просмотр
- `suppliers` — доступа нет

### Аналитик / Бухгалтер

- просмотр всех справочников и документов;
- полный просмотр отчетов.

## Описание отчетов

В приложении реализованы 4 отчета:

1. Заказы за период.
2. Финансовый отчет по договорам за период.
3. Отчет по поставщикам.
4. Просроченные поставки.

Во всех отчетах доступны:

- фильтр по диапазону дат;
- просмотр в таблице;
- экспорт в CSV;
- экспорт в XLSX.

## Seed-данные

Демо-набор включает:

- 6 поставщиков;
- 15 позиций цветов;
- 8 договоров;
- 24 заказа на поставку.

Все демонстрационные данные русскоязычные и подходят для показа преподавателю.

## Проверка проекта

Запуск тестов:

```powershell
pytest
```

## Примечания по реализации

- таблица заказов называется `purchase_orders`, чтобы не использовать зарезервированное имя `order`;
- цена в заказе фиксируется в поле `unit_price_snapshot`;
- сумма строки рассчитывается как `quantity * unit_price_snapshot`;
- итоговая сумма по договору считается с учетом `price_coefficient`;
- права доступа реализованы на уровне приложения;
- в интерфейсе используются `Treeview` и модальные окна ввода.
