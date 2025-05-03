import aiohttp
from decouple import config

employer_id = config('EMPLOYER_ID')

async def fetch_vacancies(session: aiohttp.ClientSession, employer_id: str) -> list:
    """
    Запрашивает список активных вакансий работодателя через API hh.ru
    """
    url = 'https://api.hh.ru/vacancies'
    params = {
        'employer_id': employer_id,
        'only_with_salary': 'false',
        'per_page': 10,
        'page': 0
    }
    async with session.get(url, params=params) as resp:
        resp.raise_for_status()
        data = await resp.json()
        return data.get('items', [])