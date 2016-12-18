import json
from riotAPI import RiotAPI, EUNE_ENDPOINT
from crawler import crawl


MoegamiID = 20391818


if __name__ == '__main__':
    with open('api_key.txt') as f:
        API_KEY = f.read().strip()

    riotAPI = RiotAPI(EUNE_ENDPOINT, API_KEY)

    result = crawl(riotAPI, 5, 5)
    print(json.dumps(result))