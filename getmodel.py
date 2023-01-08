import asyncio
import aiohttp
import requests


async def __get__(url, session):
    async with session.get(url=url) as response:
        resp = await response.json()
        models = []
        for i in resp:
            models.append(i.get("id"))
            
        return {"id":url[55:-7], "models":models}


async def __SessionEnginePage__(function, urls):
    dictarr = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            task = asyncio.create_task(function(url, session, ))
            dictarr.append(task)
        ret = await asyncio.gather(*dictarr)

    return ret


def getmodels():
    url = 'https://api.av.by/offer-types/cars/catalog/brand-items'
    r = requests.get(url=url)
    brands = r.json()
    urls = []

    for i in brands:
        brandId = i.get("id")
        url = f'https://api.av.by/offer-types/cars/catalog/brand-items/{brandId}/models'
        urls.append(url)

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    pages = asyncio.run(__SessionEnginePage__(__get__, urls))

    return pages

