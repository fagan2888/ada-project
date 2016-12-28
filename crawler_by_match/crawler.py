import sys
from itertools import chain
import concurrent.futures
from collections import defaultdict




# def get_random_summonerId(riotAPI):
#     r = riotAPI.featuredgames()
#     participants = chain.from_iterable(x['participants'] for x in r['gameList'])
#     summonerNames = [x['summonerName'] for x in participants if not x['bot']]
#     r2 = riotAPI.summoner(summonerNames[:1])
#     return [summonerDto['id'] for summonerDto in r2.values()][0]

def merge_dicts(old, to_add):
    for k, v in to_add.items():
        old[k] = old[k] | v


def extract_matchIds(matchList):
    if matchList['totalGames'] > 0:
        return [match['matchId'] for match in matchList['matches']]
    else:
        return[]


def extract_summonerIds(match):
    if 'participantIdentities' not in match:
        print("'participantIdentities' missing in match!", file=sys.stderr)
        print(match, file=sys.stderr)
        return []
    return {pIdentity['player']['summonerId'] for pIdentity in match['participantIdentities']}

def get_last_matches(summoners_list, matches_keys, riotAPI, matchesPerSummoner):
    def get_matchlist(sid):
        r = riotAPI.matchlist(sid)
        matchIds = extract_matchIds(r)[:matchesPerSummoner]
        return matchIds

    with concurrent.futures.ThreadPoolExecutor(max_workers = 10) as executor:
        future_to_list = {executor.submit(get_matchlist, id): id for id in summoners_list}
        player_matches = {future_to_list[future]: set(future.result()) for future in concurrent.futures.as_completed(future_to_list)}
        # set to remove duplicates
        matches_to_fetch = {match for key, sublist in player_matches.items() for match in sublist if match not in matches_keys}

    with concurrent.futures.ThreadPoolExecutor(max_workers = 50) as executor:
        future_to_match = {executor.submit(riotAPI.match, mId): mId for mId in matches_to_fetch}
        matches = {future_to_match[future]: future.result() for future in concurrent.futures.as_completed(future_to_match)}

    return (player_matches, matches)

def crawl(riotAPI, matchesPerSummoner, matchesNum, startId):
    # if startId is None:
    #     startId = get_random_summonerId(riotAPI)

    available_matches = set([startId])
    processed_matches = list()
    matches = {}
    summ_matches = defaultdict(set)

    while len(processed_matches) < matchesNum:
        mID = available_matches.pop()
        match_data = riotAPI.match(mID)
        summs_to_fetch = extract_summonerIds(match_data)

        player_matches, last_matches = get_last_matches(summs_to_fetch, matches.keys(), riotAPI, matchesPerSummoner)

        # add the current match to the list of matches with complete info (x last games of each participant)
        processed_matches.append(mID)

        # add new fetched matches_ids to players
        merge_dicts(summ_matches, player_matches)

        # add new fetched matches to global list
        matches.update(last_matches)

        # add new fetched matches ids to list of matches to fetch completely (can remove some duplication)
        available_matches = available_matches | {match for match in last_matches.keys() if match not in processed_matches}

    print(len(available_matches))
    print(processed_matches)

    return (
        processed_matches,
        summ_matches,
        matches,
    )



 # summonerId = avaiableSummoners.pop()
 #        r = riotAPI.matchlist(summonerId)
 #        matchIds = extract_matchIds(r)[:matchesPerSummoner]
 #        processedSummoners[summonerId] = matchIds
 #        newMatches = [(mId, riotAPI.match(mId)) for mId in matchIds if mId not in matches]
 #        matches.update(dict(newMatches))
 #        summonerIds = chain.from_iterable(extract_summonerIds(m[1]) for m in newMatches)
 #        newSummonerIds = [sId for sId in summonerIds if sId not in processedSummoners]
 #        avaiableSummoners.update(set(newSummonerIds))
