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
                               films=await insert_prm(person.get('films'),1),
                               gender=person.get('gender'),
                               hair_color=person.get('hair_color'),
                               height=person.get('height'),
                               homeworld=person.get('homeworld'),
                               mass=person.get('mass'),
                               skin_color=person.get('skin_color'),
                               created=person.get('created'),
                               edited=person.get('edited'),
                               species=await insert_prm(person.get('species'),2),
                               starships=await insert_prm(person.get('starships'), 3),
                               url=person.get('url'),
                               vehicles=await insert_prm(person.get('vehicles'),4)
                                ) for person in people_list_json]
    async with Session() as session:
        session.add_all(people_list)
        await session.commit()

# Создание полного списка одного из параметров(все фильмы, все специальности и др.)
# Пареметры имеющие множественное значение
async def insert_prm(json_p, prm):
    list_prm = []
    if json_p == [] or json_p is None:
        return None
    else:
        if prm == 1:
            for per in json_p:
                roster = await json_prm(per)
                list_prm.append(roster.get('title'))
            return list_prm
        elif prm == 2:
            for per in json_p:
                roster = await json_prm(per)
                list_prm.append(roster.get('name'))
            return list_prm
        elif prm == 3:
            for per in json_p:
                roster = await json_prm(per)
                list_prm.append(roster.get('starship_class'))
            return list_prm
        elif prm == 4:
            for per in json_p:
                roster = await json_prm(per)
                list_prm.append(roster.get('vehicle_class'))
            return list_prm

# Получение единицы определенного параметра героя(одного фильма, одной специальности и т.к.)
async def json_prm(json_p):
    session = aiohttp.ClientSession()
    response = await session.get(json_p)
    json_data = await response.json()
    await session.close()
    return json_data


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
