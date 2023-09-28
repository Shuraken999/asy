import asyncio
import datetime

import aiohttp
from more_itertools import chunked

from models import Base, Session, SwapiPeople, engine

MAX_REQUESTS_CHUNK = 5

# Занесение данных в БД
async def insert_people(people_list_json):
    people_list = [SwapiPeople(
                               name=person.get('name'),
                               birth_year=person.get('birth_year'),
                               eye_color=person.get('eye_color'),
                               films=person.get('films'),
                               gender=person.get('gender'),
                               hair_color=person.get('hair_color'),
                               height=person.get('height'),
                               homeworld=person.get('homeworld'),
                               mass=person.get('mass'),
                               skin_color=person.get('skin_color'),
                               created=person.get('created'),
                               edited=person.get('edited'),
                               species=person.get('species'),
                               starships=person.get('starships'),
                               url=person.get('url'),
                               vehicles=person.get('vehicles')
                                ) for person in people_list_json]
    async with Session() as session:
        session.add_all(people_list)
        await session.commit()

# Обращение за данными по конкретному герою
async def get_people(people_id):
    session = aiohttp.ClientSession()
    response = await session.get(f"https://swapi.dev/api/people/{people_id}")
    json_data = await response.json()
    await session.close()
    return json_data


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    for person_ids_chunk in chunked(range(1, 100), MAX_REQUESTS_CHUNK):
        person_coros = [get_people(person_id) for person_id in person_ids_chunk]
        people = await asyncio.gather(*person_coros)
        insert_people_coro = insert_people(people)
        asyncio.create_task(insert_people_coro)

    main_task = asyncio.current_task()
    insets_tasks = asyncio.all_tasks() - {main_task}
    await asyncio.gather(*insets_tasks)


if __name__ == "__main__":
    start = datetime.datetime.now()
    asyncio.run(main())
    print(datetime.datetime.now() - start)
