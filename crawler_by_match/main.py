import json
from riotAPI import RiotAPI, EUNE_ENDPOINT
from crawler import crawl


first_match = 1588970821


if __name__ == '__main__':
    with open('api_key.txt') as f:
        API_KEY = f.read().strip()

    riotAPI = RiotAPI(EUNE_ENDPOINT, API_KEY, 'production')

    result = crawl(riotAPI, 20, 10, first_match)
    f = open('out.json', 'w')

    def set_default(obj):
      if isinstance(obj, set):
          return list(obj)
      raise TypeError


    f.write(json.dumps(result, default=set_default))
