import json
import csv
import signal
import argparse
import pickle
import contextlib
import os
import shutil

from riotAPI import RiotAPI, EUW_ENDPOINT
from matchSaver import MatchSaver
from crawler import crawl


first_match = 3017449777


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=(
            "Crawl LOL data by match. "
            "Enter Ctrl + C to stop prematurely and save the results. "
            "In case of an exception program attempts to save the results as well. "
            "You can resume crawling later using the --resume option."))
    parser.add_argument('matchesPerSummoner', type=int)
    parser.add_argument('matchesNum', type=int)
    parser.add_argument('-d', '--directory', required=True,
                        help="The directory in which the results will be saved.")
    parser.add_argument('-r', '--resume',
                        help=("Resume crawling from results saved in the given directory. "
                              "Can be the same as the --directory argument. "
                              "Note that you should use the same matchesPerSummoner value."))
    parser.add_argument('-a', '--api-key', type=argparse.FileType('r'), default='api_key.txt',
                        help=("Specify a path to a file with Riot API key. Default: api_key.txt"))
    args = parser.parse_args()

    # Load API KEY and init riotAPI.
    with contextlib.closing(args.api_key):
        API_KEY = args.api_key.read().strip()

    riotAPI = RiotAPI(EUW_ENDPOINT, API_KEY, 'production')

    # Ensure the output directory exists.
    try:
        os.makedirs(args.directory)
    except OSError:
        pass # Already exists probably

    # Do necessary preparations for resuming if applicable.
    matchesPath = os.path.join(args.directory, 'matches.csv')
    if args.resume is None:
        prevResult = None
        matchesFile = open(matchesPath, 'w')
    else:
        prevResultPath = os.path.join(args.resume, 'result.pickle')
        with open(prevResultPath, 'rb') as f:
            prevResult = pickle.load(f)

        if args.directory != args.resume:
            shutil.copy(os.path.join(args.resume, 'matches.csv'), args.directory)

        matchesFile = open(matchesPath, 'a')

    matchSaver = MatchSaver(matchesFile)

    # Register a SIGINT handler that sets `aborted` to True.
    aborted = False
    def SIGINT_handler(signal, frame):
        global aborted
        aborted = True
    signal.signal(signal.SIGINT, SIGINT_handler)

    result = crawl(riotAPI, args.matchesPerSummoner, args.matchesNum, first_match, matchSaver, lambda: aborted, prevResult)
    processed_matches, summ_matches, matches = result
    matchesFile.close()

    os.chdir(args.directory)

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

    # pickle the result to resume the crawling later
    with open('result.pickle', 'wb') as f:
        pickle.dump(result, f, protocol=pickle.HIGHEST_PROTOCOL)
