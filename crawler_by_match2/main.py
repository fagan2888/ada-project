import json
import csv
import signal
import argparse
import pickle
import contextlib

from riotAPI import RiotAPI, EUNE_ENDPOINT
from crawler import crawl


first_match = 1588970821


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=(
            "Crawl LOL data by match. "
            "Enter Ctrl + C to stop prematurely and save results. "
            "You can resume later using the --resume option."))
    parser.add_argument('matchesPerSummoner', type=int)
    parser.add_argument('matchesNum', type=int)
    parser.add_argument('-r', '--resume', dest='file', type=argparse.FileType('rb'),
                        help=("Resume crawling from a pickled result. "
                              "Note that you should use the same matchesPerSummoner value."))

    parser.add_argument('-a', '--api-key', type=argparse.FileType('r'), default='api_key.txt',
                        help=("Specify path to a file with Riot API key. Default: api_key.txt"))
    parser.add_argument('-p', '--prefix', default='',
                        help="Prefix the names of created files with PREFIX")
    args = parser.parse_args()

    if args.file is None:
        prevResult = None
    else:
        with contextlib.closing(args.file):
            prevResult = pickle.load(args.file)

    with contextlib.closing(args.api_key):
        API_KEY = args.api_key.read().strip()

    riotAPI = RiotAPI(EUNE_ENDPOINT, API_KEY, 'production')


    # Register a SIGINT handler that sets `aborted` to True.
    aborted = False
    def SIGINT_handler(signal, frame):
        global aborted
        aborted = True
    signal.signal(signal.SIGINT, SIGINT_handler)


    result = crawl(riotAPI, args.matchesPerSummoner, args.matchesNum, first_match, lambda: aborted, prevResult)
    processed_matches, summ_matches, matches = result

    def set_default(obj):
      if isinstance(obj, set):
          return list(obj)
      raise TypeError

    def processParticipant(participant):
      return [
        participant['summonerId'],
        participant['lane'],
        participant['role'],
        participant['team'],
        participant['winner'],
        participant['goldEarned'],
        participant['kills'],
        participant['deaths'],
        participant['assists'],
        participant['largestKillingSpree'],
        participant['totalDamageDealt'],
        participant['totalDamageDealtToChampions'],
        participant['totalDamageTaken'],
        participant['totalTimeCrowdControlDealt'],
        participant['csDiff10'],
        participant['cs10'],
        participant['gpm10'],
        participant['xpDiff10'],
        participant['csDiff20'],
        participant['cs20'],
        participant['gpm20'],
        participant['xpDiff20']
      ]

    def matchToList(o):
      fixed = [
        o['matchId'],
        o['matchDuration'],
        o['region'],
        o['queueType']
      ]
      participants = [item for participant in o['participants'] for item in processParticipant(participant)]

      return fixed + participants

    p = args.prefix
    # processed matches
    with open(p + 'processed_matches.json', 'w') as f:
      processed_matches_arr = [{"p_match_id": str(id)} for id in processed_matches]
      f.write(json.dumps(processed_matches_arr, default = set_default))

    # summoner to match link
    with open(p + 'summ_matches.json', 'w') as f:
      summ_matches_arr = [{"summ_id": str(key), "matches": value} for key, value in summ_matches.items()]
      f.write(json.dumps(summ_matches_arr, default = set_default))

    # matches
    with open(p + 'matches.csv', 'w') as f:
      matches_arr = [matchToList(value) for key, value in matches.items()]
      csvWriter = csv.writer(f, delimiter=',', lineterminator='\n')
      csvWriter.writerows(matches_arr)

    # pickle the result to resume the crawling later
    with open(p + 'result.pickle', 'wb') as f:
        pickle.dump(result, f, protocol=pickle.HIGHEST_PROTOCOL)
