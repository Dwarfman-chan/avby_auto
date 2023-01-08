from bs4 import BeautifulSoup
import asyncio
import aiohttp
import time
import numpy as np
import pandas as pd
from pagecounter import pagecounter
from apiasync import asyncapi


async def get(url, session):

    data = []

    while True:
        try:
            async with session.get(url=url) as response:
                resp = await response.text()
                soup = BeautifulSoup(resp, "html.parser").main

                for wrap in soup.find_all('div', class_='listing-item__wrap'):

                    mask_url = "https://cars.av.by"
                    id_arr = wrap.find_all('a', href=True)
                    id = id_arr[0].get('href').split('/')[3]
                    url = mask_url + id_arr[0].get('href')
                    brand = id_arr[0].text

                    params = wrap.find_all(
                        'div', class_='listing-item__params')[0].find_all()
                    year = params[0].text
                    shortdesc = params[1].text
                    mileage = params[2].text

                    price = wrap.find('div', class_='listing-item__price').text
                    priceusd = wrap.find(
                        'div', class_='listing-item__priceusd').text[2:]

                    message = wrap.find('div', class_='listing-item__message')

                    if message:
                        descript = message.text.replace(
                            '\n', ' ').replace('\r', ' ')
                    else:
                        descript = None

                    data.append([id, url, brand, year, shortdesc,
                                mileage, price, priceusd, descript])

                print("Successfully got url {} status {}.".format(
                    url, response.status))

                return data

        except Exception:
            print("Exception find")
            pass


async def SessionEnginePage(function, urls):
    # data = np.array([]).reshape(0, 9)
    dictarr = []
    jugg = []

    async with aiohttp.ClientSession() as session:
        for url in urls:
            task = asyncio.create_task(function(url, session))
            dictarr.append(task)

        ret = await asyncio.gather(*dictarr)

        for i in ret:
            for j in i:
                jugg.append(j)
            # data = np.concatenate([data, i])

    print("\nFinalized all. Return is a list of len {} outputs.".format(len(ret)))
    return jugg


def main():
    pageids = pagecounter()

    urls = []

    for i in pageids:
        brandId = i.get("brandId")
        modelId = i.get("modelId")
        for page in range(1, i.get("pages")+1):
            url = f'https://cars.av.by/filter?brands[0][brand]={brandId}&brands[0][model]={modelId}&page={page}'
            urls.append(url)

    print(len(urls))

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    start = time.time()
    pages = asyncio.run(SessionEnginePage(get, urls))
    end = time.time()

    print(end-start)
    print(len(pages))

    columns = ["Id", "Url", "Brand", "Year", "Description",
               "Mileage", "Price", "Priceusd", "Message"]
    df = pd.DataFrame(pages, columns=columns)
    ids = df['Id'].values.tolist()

    json = asyncapi(ids)

    date = []
    name = []

    for i in ids:
        if json[str(i)] is not None:
            date.append(json[str(i)][0])
            name.append(json[str(i)][1])
        else:
            print(i)
            date.append(None)
            name.append(None)

    df.insert(1, 'Date', date)
    df.insert(2, 'Name', name)
    
    df.to_csv(
        "av2.csv", sep=";", mode='w', index=False)


if __name__ == "__main__":
    main()
