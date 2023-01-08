import asyncio
import aiohttp
import time
import numpy as np
import pandas as pd
import json


async def get(url, session):
    dictrow = {}
    bool = True

    while bool:

        async with session.get(url=url) as response:
            id = url.split('/')[-1]
            if response.status == 200:

                resp = await response.json()
                publite = resp.get("publishedAt")
                name = resp.get("sellerName")

                dictrow[id] = [publite, name]
                bool = False

            elif response.status == 404:
                print("StatusCode: ", response.status)

                dictrow[id] = None
                bool = False

            else:
                print("SomeotherMisstake", response.status)

        return dictrow


async def SessionEnginePage(function, urls):
    dictarr = []
    dict = {}

    async with aiohttp.ClientSession() as session:
        for url in urls:
            task = asyncio.create_task(function(url, session))
            dictarr.append(task)
        ret = await asyncio.gather(*dictarr)

    print("\nFinalized all. Return is a list of len {} outputs.".format(len(ret)))
    
    for i in ret:
        dict.update(i)
    return dict


def asyncapi(ids):
    # df = pd.read_csv('av2.csv', sep=';', header=0)
    # ids = df['Id'].values.tolist()

    urls = []

    for url in ids:
        link = f"https://api.av.by/offers/{url}"
        urls.append(link)

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    start = time.time()
    pages = asyncio.run(SessionEnginePage(get, urls)) 
    end = time.time()

    print(end-start)

    return pages

    # with open('json.json', 'w', encoding='utf-8') as f:
    #     f.write(json.dumps(pages, indent=4))
