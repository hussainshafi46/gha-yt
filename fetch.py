import aiohttp
import asyncio
import json
import sys
import random
from pprint import pprint

API_BASE_URL = "https://genius.com/api/artists/{artist_id}/songs?page={page}&per_page=50&sort=title"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
}
PROXIES = {
    "http": "http://186.190.225.152:999",
    "https": "http://186.190.225.152:999"
}
MAX_CONCURRENT_REQUESTS = 5  # Limit concurrent requests to avoid overloading the API

async def fetch_page(session, artist_id, page, semaphore):
    """Fetch a single page of songs asynchronously."""
    url = API_BASE_URL.format(artist_id=artist_id, page=page)
    
    async with semaphore:  # Limit concurrency
        await asyncio.sleep(random.uniform(1, 3))  # Rate limiting (random delay)
        
        try:
            async with session.get(url, headers=HEADERS, proxy=PROXIES["https"]) as response:
                response.raise_for_status()
                data = await response.json()

                if "response" not in data or "songs" not in data["response"]:
                    print(f"Unexpected response format: {data}")
                    return None

                return data["response"]
        
        except aiohttp.ClientError as e:
            print(f"Request failed for {url}: {e}")
            return None
        except json.JSONDecodeError:
            print(f"Failed to parse JSON response from {url}")
            return None

async def fetch_songs(artist_id):
    """Fetch all songs for an artist asynchronously."""
    results = []
    next_page = 1
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)  # Limit concurrent requests

    async with aiohttp.ClientSession() as session:
        while next_page:
            response = await fetch_page(session, artist_id, next_page, semaphore)
            if not response or not response.get("songs"):
                break

            results.extend(response["songs"])
            next_page = response.get("next_page", None)  # Handle missing key safely

    # Print JSON output with 4-space indentation
    pprint(results, indent=4)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python script.py <artist_id> <artist_name>")
        sys.exit(1)

    _, artist_id, artist_name = sys.argv
    asyncio.run(fetch_songs(artist_id))

