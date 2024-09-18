import json
import sys
from requests import get
from bs4 import BeautifulSoup

initial = "A"

with open(f"pages/{initial}.txt", 'r', encoding='utf-8') as f:
    pageNumber = int(f.read().strip())
if pageNumber == 0:
    print(f"COMPLETED FETCHING {initial}")
    sys.exit(0)

artists = {}
try:
    with open(f"artists/{initial}.json", 'r', encoding='utf-8') as f:
        artists |= json.load(f)
except:
    pass

while pageNumber:
    print(f"Query Page ({initial}):", pageNumber)
    try:
        response = get(url=f'https://genius.com/artists-index/{initial}/all?page={pageNumber}')
        print("Query Status:", response.status_code)
        if response.status_code != 200:
            break
        soup = BeautifulSoup(response.content, 'lxml')
        artist_lists = soup.find_all("ul", class_="artists_index_list")
        for artist_list in artist_lists:
            for list_item in artist_list.find_all("li"):
                a_tag = list_item.find_next("a")
                artists[a_tag.get_text(strip=True).strip()] = a_tag['href']
        if soup.find("div", class_="pagination"):
            pageNumber += 1
        else:
            pageNumber = 0
    except Exception as e:
        print(e)
        break

with open(f"artists/{initial}.json", 'w', encoding='utf-8') as f:
    json.dump(artists, f, indent=2)
with open(f"pages/{initial}.txt", 'w', encoding='utf-8') as f:
    f.write(str(pageNumber))