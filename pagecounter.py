from bs4 import BeautifulSoup
import asyncio
import aiohttp
import re
import time
from getmodel import getmodels
import json


async def get(url, session):
    while True:
        try:
            async with session.get(url=url[0]) as response:

                resp = await response.text()

                soup = BeautifulSoup(resp, "html.parser").form
                req_ads = soup.find(
                    'button', class_="button button--secondary button--block")

                if any(map(str.isdigit, req_ads.text)):
                    total = int(re.sub(r'[^0-9]+', r'', req_ads.text))
                    if total % 25 == 0:
                        pages = total // 25
                    elif total % 25 != 0:
                        pages = total // 25 + 1

                    print("Successfully got url {} status {}.".format(
                        url[0], response.status))
                        
                    return {"brandId": url[1], "modelId": url[2], "pages": pages}
                else:
                    return None

        except Exception:
            print("Exception find")
            pass


async def SessionEnginePage(function, urls):
    dictarr = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            task = asyncio.create_task(function(url, session))
            dictarr.append(task)
        ret = await asyncio.gather(*dictarr)

    print("\nFinalized all. Return is a list of len {} outputs.".format(len(ret)))
    return ret


def pagecounter():
    start = time.time()
    idictid = getmodels()
    urls = []

    for i in idictid:
        brandId = i.get("id")

        for modelId in i.get("models"):
            link = f'https://cars.av.by/filter?brands[0][brand]={brandId}&brands[0][model]={modelId}&page=1'
            urls.append([link, brandId, modelId])

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Delete array slice if exist
    pages = asyncio.run(SessionEnginePage(get, urls)) 
    end = time.time()

    while None in pages:
        pages.remove(None)

    print("\nTook {} seconds to pull.\n".format(end - start))

    with open('templog.json', 'w') as f:
        f.write(json.dumps(pages, indent=4))
    return pages

