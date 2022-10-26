from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

num_pages = 73
f = open("companies_list.txt", "a", encoding="UTF8")
f.seek(0)

for i in tqdm(range(1, num_pages)):
    r = requests.get(f'https://companiesmarketcap.com/page/{i}/')

    soup = BeautifulSoup(r.content, 'html.parser')
    table = soup.find(lambda tag: tag.name=='table')
    rows = table.findAll(lambda tag: tag.name=='tr')
    for r in rows[1:]:
        name = [i.text.strip() for i in r.find_all("div", class_="company-name")][0]
        f.write(name+"\n")

f.close()