import json
from riotAPI import RiotAPI, EUNE_ENDPOINT
from crawler import crawl


first_match = 1588970821


if __name__ == '__main__':
    with open('api_key.txt') as f:
        API_KEY = f.read().strip()

    riotAPI = RiotAPI(EUNE_ENDPOINT, API_KEY, 'production')

    processed_matches, summ_matches, matches = crawl(riotAPI, 20, 100, first_match)



    def set_default(obj):
      if isinstance(obj, set):
          return list(obj)
      raise TypeError

    # processed matches
    with open('processed_matches.json', 'w') as f:
      processed_matches_arr = [{"p_match_id": str(id)} for id in processed_matches]
      f.write(json.dumps(processed_matches_arr, default = set_default))

    # summoner to match link
    with open('summ_matches.json', 'w') as f:
      summ_matches_arr = [{"summ_id": str(key), "matches": value} for key, value in summ_matches.items()]
      f.write(json.dumps(summ_matches_arr, default = set_default))

    # matches
    with open('matches.json', 'w') as f:
      matches_arr = [value for key, value in matches.items()]
      f.write(json.dumps(matches_arr, default = set_default))
