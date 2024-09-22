from requests import get
from pprint import pprint
from json import dump
from sys import argv

def fetchSongs(artist_id, atrist_name):
    results = []
    next_page = 1
    while next_page:
        songs_api = f'https://genius.com/api/artists/{artist_id}/songs?page={next_page}&per_page=50&sort=title'
        try:
            resp = get(songs_api, headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"}, proxies={'http':'186.190.225.152:999', 'https':'186.190.225.152:999'}).json()
            pprint(resp)
            meta = resp['meta']
            #assert meta['status'] == 200
            next_page = resp['response']['next_page']
            results.extend(resp['response']['songs'])
        except Exception as e:
            print("EXCEPTION: ", songs_api)
            print("Error is:", e)
            break
    with open(f"{atrist_name}.json", 'w', encoding='utf-8') as f:
        dump(results, f, indent=4)

if __name__ == '__main__':
    _, a_id, a_name = argv
    fetchSongs(a_id, a_name)