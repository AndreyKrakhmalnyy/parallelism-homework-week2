from datetime import datetime, timedelta
from app.infrastructure.postgres.models import Event, EventSeat, Location, Seat
from app.infrastructure.postgres.manager import DatabaseManager
from sqlalchemy import func, select


async def add_event_data_to_db(db_manager: DatabaseManager) -> None:
    if await db_manager.session.scalar(select(func.count(Location.id))):
        print("Тестовые данные уже существуют")
        return

    location = Location(
        name="Центральный зал",
        city="Москва",
        address="Тверская улица, 1",
    )
    db_manager.session.add(location)
    await db_manager.session.flush()

    seats = []
    for row in range(1, 6):
        for number in range(1, 11):
            seats.append(
                Seat(
                    location_id=location.id,
                    sector="Основной сектор",
                    row=row,
                    number=number,
                    x=number * 50,
                    y=row * 50,
                )
            )
    db_manager.session.add_all(seats)
    await db_manager.session.flush()

    event = Event(
        organizer_id=1,
        location_id=location.id,
        title="Python Конференция",
        description="Тестовое мероприятие для домашнего задания",
        category="конференция",
        starts_at=datetime.now() + timedelta(days=30),
        base_price=5000,
    )
    db_manager.session.add(event)
    await db_manager.session.flush()

    db_manager.session.add_all(
        EventSeat(event_id=event.id, seat_id=seat.id, price=event.base_price)
        for seat in seats
    )
    await db_manager.commit()

    print("Тестовые данные созданы")


if __name__ == "__main__":
    import asyncio

    from app.config import settings
    from app.ioc import create_container

    async def _main() -> None:
        container = create_container(settings)
        async with container() as request_container:
            db_manager = await request_container.get(DatabaseManager)
            await add_event_data_to_db(db_manager)
        await container.close()

    asyncio.run(_main())
