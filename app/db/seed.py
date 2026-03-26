from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.models.contract import Contract
from app.models.flower import Flower
from app.models.purchase_order import PurchaseOrder
from app.models.supplier import Supplier


def _amount(quantity: str, unit_price: Decimal) -> Decimal:
    return (Decimal(quantity) * unit_price).quantize(Decimal("0.01"))


def seed_database(session_factory: sessionmaker[Session]) -> None:
    with session_factory() as session:
        if session.scalar(select(Supplier.id).limit(1)) is not None:
            return

        suppliers = [
            Supplier(name="ООО Зеленый Мир", contact_person="Светлана Трофимова", phone="+7 (343) 301-11-20", email="info@greenworld.ru", address="г. Екатеринбург, ул. Шефская, 45", inn="6671453201", is_active=True),
            Supplier(name="ИП Питомник Ромашково", contact_person="Павел Дементьев", phone="+7 (912) 220-40-15", email="sales@romashkovo.ru", address="Свердловская обл., с. Кашино, ул. Полевая, 7", inn="665812345678", is_active=True),
            Supplier(name="ООО Флора-Снаб", contact_person="Елена Горская", phone="+7 (343) 355-44-10", email="manager@flora-snab.ru", address="г. Екатеринбург, ул. Монтажников, 12", inn="6679021140", is_active=True),
            Supplier(name="ООО УралСадПоставка", contact_person="Григорий Невский", phone="+7 (922) 145-80-99", email="office@uralsad.ru", address="г. Первоуральск, ул. Ленина, 51", inn="6625017799", is_active=True),
            Supplier(name="ООО Ботаника Плюс", contact_person="Дарья Колосова", phone="+7 (343) 289-77-31", email="mail@botanika-plus.ru", address="г. Тюмень, ул. Холодильная, 96", inn="7203378456", is_active=True),
            Supplier(name="ООО Северный Тепличный Комплекс", contact_person="Илья Королев", phone="+7 (3452) 61-15-80", email="supply@north-green.ru", address="г. Тюмень, ул. Авторемонтная, 18", inn="7204188821", is_active=False),
        ]
        session.add_all(suppliers)
        session.flush()

        supplier_by_name = {supplier.name: supplier for supplier in suppliers}
        flowers = [
            Flower(supplier_id=supplier_by_name["ООО Зеленый Мир"].id, name="Петуния", variety="Ампельная", color="Розовый", unit="шт", purchase_price=Decimal("45.00"), min_batch=20, season="весна-лето", notes="Подходит для подвесных кашпо", is_active=True),
            Flower(supplier_id=supplier_by_name["ООО Зеленый Мир"].id, name="Бархатцы", variety="Отклоненные", color="Оранжевый", unit="кассета", purchase_price=Decimal("320.00"), min_batch=5, season="весна-лето", notes="Хорошо переносят жару", is_active=True),
            Flower(supplier_id=supplier_by_name["ИП Питомник Ромашково"].id, name="Роза", variety="Флорибунда", color="Красный", unit="шт", purchase_price=Decimal("280.00"), min_batch=10, season="весна", notes="С закрытой корневой системой", is_active=True),
            Flower(supplier_id=supplier_by_name["ИП Питомник Ромашково"].id, name="Хоста", variety="Патриот", color="Зелено-белый", unit="шт", purchase_price=Decimal("190.00"), min_batch=12, season="весна-лето", notes="Теневыносливое растение", is_active=True),
            Flower(supplier_id=supplier_by_name["ООО Флора-Снаб"].id, name="Сальвия", variety="Блестящая", color="Красный", unit="кассета", purchase_price=Decimal("360.00"), min_batch=4, season="лето", notes="Для городских клумб", is_active=True),
            Flower(supplier_id=supplier_by_name["ООО Флора-Снаб"].id, name="Алиссум", variety="Снежный ковер", color="Белый", unit="кассета", purchase_price=Decimal("295.00"), min_batch=4, season="весна-лето", notes="Заполняет края цветников", is_active=True),
            Flower(supplier_id=supplier_by_name["ООО УралСадПоставка"].id, name="Тюльпан", variety="Триумф", color="Желтый", unit="лоток", purchase_price=Decimal("980.00"), min_batch=3, season="осень", notes="Луковицы для осенней высадки", is_active=True),
            Flower(supplier_id=supplier_by_name["ООО УралСадПоставка"].id, name="Нарцисс", variety="Крупнокорончатый", color="Желто-белый", unit="лоток", purchase_price=Decimal("870.00"), min_batch=3, season="осень", notes="Луковичные культуры", is_active=True),
            Flower(supplier_id=supplier_by_name["ООО Ботаника Плюс"].id, name="Виола", variety="Швейцарские гиганты", color="Фиолетовый", unit="кассета", purchase_price=Decimal("340.00"), min_batch=5, season="весна", notes="Для раннего оформления", is_active=True),
            Flower(supplier_id=supplier_by_name["ООО Ботаника Плюс"].id, name="Бегония", variety="Вечноцветущая", color="Белый", unit="шт", purchase_price=Decimal("68.00"), min_batch=30, season="лето", notes="Для контейнерного озеленения", is_active=True),
            Flower(supplier_id=supplier_by_name["ООО Зеленый Мир"].id, name="Колеус", variety="Блюма", color="Бордовый", unit="шт", purchase_price=Decimal("62.00"), min_batch=25, season="лето", notes="Декоративно-лиственное растение", is_active=True),
            Flower(supplier_id=supplier_by_name["ООО Флора-Снаб"].id, name="Цинерария", variety="Сильвер Даст", color="Серебристый", unit="шт", purchase_price=Decimal("58.00"), min_batch=20, season="лето", notes="Для бордюрной посадки", is_active=True),
            Flower(supplier_id=supplier_by_name["ООО УралСадПоставка"].id, name="Георгина", variety="Микс", color="Микс", unit="шт", purchase_price=Decimal("115.00"), min_batch=15, season="весна-лето", notes="Крупные яркие соцветия", is_active=True),
            Flower(supplier_id=supplier_by_name["ООО Ботаника Плюс"].id, name="Лобелия", variety="Ампельная", color="Синий", unit="шт", purchase_price=Decimal("52.00"), min_batch=40, season="весна-лето", notes="Для подвесных композиций", is_active=True),
            Flower(supplier_id=supplier_by_name["ООО Северный Тепличный Комплекс"].id, name="Хризантема", variety="Мультифлора", color="Желтый", unit="шт", purchase_price=Decimal("130.00"), min_batch=15, season="осень", notes="Поставщик временно неактивен", is_active=False),
        ]
        session.add_all(flowers)
        session.flush()

        flower_by_key = {f"{flower.name}:{flower.variety}": flower for flower in flowers}
        contracts = [
            Contract(contract_number="ДОГ-2026-001", contract_date=date(2026, 1, 15), customer_name="МАУ Парк Культуры и Отдыха", customer_phone="+7 (343) 200-10-10", customer_email="park@ekb.ru", object_name="Оформление входной группы парка", object_address="г. Екатеринбург, ул. Мичурина, 230", start_date=date(2026, 4, 10), end_date=date(2026, 5, 30), price_coefficient=Decimal("1.20"), status="active", notes="Весеннее озеленение"),
            Contract(contract_number="ДОГ-2026-002", contract_date=date(2026, 1, 20), customer_name="Администрация Верх-Исетского района", customer_phone="+7 (343) 371-22-45", customer_email="viset@ekadm.ru", object_name="Цветники у районной администрации", object_address="г. Екатеринбург, ул. Московская, 27", start_date=date(2026, 4, 15), end_date=date(2026, 6, 15), price_coefficient=Decimal("1.15"), status="active", notes="Контракт с несколькими этапами поставки"),
            Contract(contract_number="ДОГ-2026-003", contract_date=date(2026, 2, 3), customer_name="ООО ТЦ Север", customer_phone="+7 (343) 290-55-77", customer_email="office@tc-sever.ru", object_name="Входная группа торгового центра", object_address="г. Екатеринбург, пр. Космонавтов, 86", start_date=date(2026, 5, 1), end_date=date(2026, 5, 25), price_coefficient=Decimal("1.35"), status="draft", notes="Ожидается подтверждение дизайна"),
            Contract(contract_number="ДОГ-2026-004", contract_date=date(2026, 2, 12), customer_name="МКУ Городское благоустройство", customer_phone="+7 (343) 376-40-80", customer_email="gbu@city.ru", object_name="Озеленение центральной площади", object_address="г. Екатеринбург, пл. 1905 года", start_date=date(2026, 5, 10), end_date=date(2026, 7, 15), price_coefficient=Decimal("1.28"), status="active", notes="Крупный муниципальный объект"),
            Contract(contract_number="ДОГ-2026-005", contract_date=date(2026, 2, 18), customer_name="АО Урал Бизнес Центр", customer_phone="+7 (343) 310-11-90", customer_email="service@ubc.ru", object_name="Ландшафтное оформление бизнес-центра", object_address="г. Екатеринбург, ул. Куйбышева, 44", start_date=date(2026, 4, 20), end_date=date(2026, 6, 1), price_coefficient=Decimal("1.18"), status="completed", notes="Закрыт досрочно"),
            Contract(contract_number="ДОГ-2026-006", contract_date=date(2026, 2, 27), customer_name="МАДОУ Детский сад № 125", customer_phone="+7 (343) 245-66-02", customer_email="sad125@edu.ru", object_name="Оформление клумб на территории детского сада", object_address="г. Екатеринбург, ул. Библиотечная, 70", start_date=date(2026, 5, 5), end_date=date(2026, 5, 28), price_coefficient=Decimal("1.10"), status="active", notes="Без растений с колючками"),
            Contract(contract_number="ДОГ-2026-007", contract_date=date(2026, 3, 1), customer_name="ЖК Солнечный квартал", customer_phone="+7 (343) 312-88-14", customer_email="uk@solnechny.ru", object_name="Озеленение дворовой территории", object_address="г. Екатеринбург, ул. Лучистая, 12", start_date=date(2026, 5, 15), end_date=date(2026, 7, 10), price_coefficient=Decimal("1.22"), status="active", notes="Много контейнерных посадок"),
            Contract(contract_number="ДОГ-2026-008", contract_date=date(2026, 3, 5), customer_name="ООО Атриум Отель", customer_phone="+7 (343) 355-90-60", customer_email="sales@atrium-hotel.ru", object_name="Сезонное оформление фасада отеля", object_address="г. Екатеринбург, ул. Куйбышева, 44д", start_date=date(2026, 5, 12), end_date=date(2026, 6, 20), price_coefficient=Decimal("1.30"), status="cancelled", notes="Отменен по инициативе заказчика"),
        ]
        session.add_all(contracts)
        session.flush()

        contract_by_number = {contract.contract_number: contract for contract in contracts}
        order_specs = [
            ("ДОГ-2026-001", "Петуния:Ампельная", "240", date(2026, 3, 10), date(2026, 4, 8), None, "approved", "Первая волна поставки"),
            ("ДОГ-2026-001", "Алиссум:Снежный ковер", "12", date(2026, 3, 11), date(2026, 4, 9), None, "ordered", ""),
            ("ДОГ-2026-001", "Лобелия:Ампельная", "180", date(2026, 3, 12), date(2026, 4, 10), None, "created", ""),
            ("ДОГ-2026-002", "Бархатцы:Отклоненные", "10", date(2026, 3, 13), date(2026, 4, 14), None, "approved", ""),
            ("ДОГ-2026-002", "Сальвия:Блестящая", "8", date(2026, 3, 14), date(2026, 4, 15), None, "created", ""),
            ("ДОГ-2026-002", "Цинерария:Сильвер Даст", "150", date(2026, 3, 15), date(2026, 4, 16), None, "created", ""),
            ("ДОГ-2026-003", "Бегония:Вечноцветущая", "300", date(2026, 3, 16), date(2026, 4, 25), None, "created", "Проектный резерв"),
            ("ДОГ-2026-003", "Колеус:Блюма", "120", date(2026, 3, 17), date(2026, 4, 26), None, "created", ""),
            ("ДОГ-2026-003", "Лобелия:Ампельная", "220", date(2026, 3, 18), date(2026, 4, 27), None, "created", ""),
            ("ДОГ-2026-004", "Роза:Флорибунда", "60", date(2026, 3, 19), date(2026, 5, 5), None, "approved", "Акцентные посадки"),
            ("ДОГ-2026-004", "Петуния:Ампельная", "320", date(2026, 3, 20), date(2026, 5, 6), None, "ordered", ""),
            ("ДОГ-2026-004", "Бархатцы:Отклоненные", "14", date(2026, 3, 20), date(2026, 5, 7), None, "approved", ""),
            ("ДОГ-2026-004", "Виола:Швейцарские гиганты", "9", date(2026, 3, 21), date(2026, 5, 8), None, "created", ""),
            ("ДОГ-2026-005", "Хоста:Патриот", "45", date(2026, 2, 25), date(2026, 4, 10), date(2026, 4, 9), "delivered", ""),
            ("ДОГ-2026-005", "Георгина:Микс", "70", date(2026, 2, 26), date(2026, 4, 11), date(2026, 4, 10), "delivered", ""),
            ("ДОГ-2026-005", "Сальвия:Блестящая", "6", date(2026, 2, 27), date(2026, 4, 12), date(2026, 4, 13), "delivered", "Поставка с задержкой на 1 день"),
            ("ДОГ-2026-006", "Бархатцы:Отклоненные", "4", date(2026, 3, 5), date(2026, 4, 28), None, "approved", ""),
            ("ДОГ-2026-006", "Алиссум:Снежный ковер", "6", date(2026, 3, 6), date(2026, 4, 29), None, "created", ""),
            ("ДОГ-2026-006", "Виола:Швейцарские гиганты", "5", date(2026, 3, 6), date(2026, 4, 30), None, "created", ""),
            ("ДОГ-2026-007", "Петуния:Ампельная", "280", date(2026, 3, 22), date(2026, 5, 12), None, "created", ""),
            ("ДОГ-2026-007", "Бегония:Вечноцветущая", "350", date(2026, 3, 22), date(2026, 5, 13), None, "approved", ""),
            ("ДОГ-2026-007", "Колеус:Блюма", "180", date(2026, 3, 23), date(2026, 5, 14), None, "created", ""),
            ("ДОГ-2026-008", "Лобелия:Ампельная", "90", date(2026, 3, 24), date(2026, 5, 10), None, "cancelled", "Заказ отменен"),
            ("ДОГ-2026-008", "Цинерария:Сильвер Даст", "80", date(2026, 3, 24), date(2026, 5, 10), None, "cancelled", ""),
        ]

        orders = []
        for contract_number, flower_key, quantity, order_date_value, planned_date, actual_date, status, notes in order_specs:
            flower = flower_by_key[flower_key]
            orders.append(
                PurchaseOrder(
                    contract_id=contract_by_number[contract_number].id,
                    flower_id=flower.id,
                    quantity=Decimal(quantity),
                    unit_price_snapshot=flower.purchase_price,
                    line_amount=_amount(quantity, flower.purchase_price),
                    order_date=order_date_value,
                    planned_delivery_date=planned_date,
                    actual_delivery_date=actual_date,
                    status=status,
                    notes=notes,
                )
            )

        session.add_all(orders)
        session.commit()
