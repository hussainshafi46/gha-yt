import aiohttp
import asyncio
import json
import sys
import random
import logging
from pprint import pprint

# Configure logging
logging.basicConfig(
    filename="fetch_songs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

API_BASE_URL = "https://genius.com/api/artists/{artist_id}/songs?page={page}&per_page=50&sort=title"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
}
MAX_CONCURRENT_REQUESTS = 5  # Limit concurrent requests to avoid overloading the API

async def fetch_page(session, artist_id, page, semaphore):
    """Fetch a single page of songs asynchronously."""
    url = API_BASE_URL.format(artist_id=artist_id, page=page)
    
    async with semaphore:  # Limit concurrency
        delay = random.uniform(1, 3)
        logging.info(f"Waiting {delay:.2f} seconds before requesting page {page}")
        await asyncio.sleep(delay)  # Rate limiting (random delay)
        
        try:
            async with session.get(url, headers=HEADERS) as response:
                logging.info(f"Fetching page {page} - Status: {response.status}")
                response.raise_for_status()
                data = await response.json()

                if "response" not in data or "songs" not in data["response"]:
                    logging.warning(f"Unexpected response format for page {page}: {data}")
                    return None

                return data["response"]
        
        except aiohttp.ClientError as e:
            logging.error(f"Request failed for {url}: {e}")
            return None
        except json.JSONDecodeError:
            logging.error(f"Failed to parse JSON response from {url}")
            return None

async def fetch_songs(artist_id):
    """Fetch all songs for an artist asynchronously."""
    results = []
    next_page = 1
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)  # Limit concurrent requests

    async with aiohttp.ClientSession() as session:
        while next_page:
            logging.info(f"Fetching songs for artist {artist_id}, page {next_page}")
            response = await fetch_page(session, artist_id, next_page, semaphore)
            if not response or not response.get("songs"):
                logging.warning(f"No songs found for page {next_page}. Stopping.")
                break

            results.extend(response["songs"])
            next_page = response.get("next_page", None)  # Handle missing key safely

    # Print JSON output with 4-space indentation
    pprint(results, indent=4)
    logging.info(f"Fetched {len(results)} songs for artist {artist_id}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python script.py <artist_id> <artist_name>")
        logging.error("Invalid arguments provided. Expected: python script.py <artist_id> <artist_name>")
        sys.exit(1)

    _, artist_id, artist_name = sys.argv
    logging.info(f"Starting song fetch for artist: {artist_name} (ID: {artist_id})")
    asyncio.run(fetch_songs(artist_id))
    logging.info("Script execution completed.")

