from cachetools import TTLCache
import aiohttp
import asyncio
import logging

# Кэш с временем жизни 600 секунд и максимальным размером 100000 элементов
leaderboard_cache = TTLCache(maxsize=100000, ttl=600)


# Функция для логирования
def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logging.getLogger('aiohttp.client').setLevel(logging.WARNING)

# Функция для получения данных с лидерборда
async def fetch_leaderboard_data(session, region, page):
    url = 'https://hearthstone.blizzard.com/ru-ru/api/community/leaderboardsData'
    params = {
        'region': region,
        'leaderboardId': 'battlegrounds',
        'page': str(page)
    }
    try:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                rows = data['leaderboard']['rows']
                if rows:
                    for row in rows:
                        row['region'] = region
                    return rows
            else:
                logging.warning(f"Failed to fetch data: HTTP {response.status} for {region}, page {page}")
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
    return []


async def update_database():
    regions = ['EU', 'AP', 'US']
    all_data = []

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        tasks = []
        for region in regions:
            for page in range(1, 50):
                tasks.append(fetch_leaderboard_data(session, region, page))

        region_data = await asyncio.gather(*tasks)
        all_data.extend([item for sublist in region_data if sublist for item in sublist])

    # Обновляем кэш
    leaderboard_cache.clear()
    for item in all_data:
        key = (item['region'], item['accountid'])
        leaderboard_cache[key] = item

    logging.info('Leaderboard cache updated!')


# Основной цикл
async def db_main():
    setup_logging()
    while True:
        logging.info('Updating the database...')
        await update_database()
        await asyncio.sleep(600)

if __name__ == "__main__":
    asyncio.run(db_main())
