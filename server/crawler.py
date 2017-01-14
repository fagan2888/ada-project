import sys
from itertools import chain
import concurrent.futures
from collections import defaultdict

from functools import reduce  # forward compatibility for Python 3
import operator

def getFromDict(dataDict, mapList):
    return reduce(operator.getitem, mapList, dataDict)




# def get_random_summonerId(riotAPI):
#     r = riotAPI.featuredgames()
#     participants = chain.from_iterable(x["participants"] for x in r["gameList"])
#     summonerNames = [x["summonerName"] for x in participants if not x["bot"]]
#     r2 = riotAPI.summoner(summonerNames[:1])
#     return [summonerDto["id"] for summonerDto in r2.values()][0]

allowed_queue_types = (
    "NORMAL_5x5_BLIND",
    "RANKED_SOLO_5x5",
    "RANKED_PREMADE_5x5",
    "NORMAL_5x5_DRAFT",
    "RANKED_TEAM_5x5",
    "TEAM_BUILDER_DRAFT_UNRANKED_5x5",
    "TEAM_BUILDER_DRAFT_RANKED_5x5",
    "TEAM_BUILDER_RANKED_SOLO",
    "RANKED_FLEX_SR"
    )

def merge_dicts(old, to_add):
    for k, v in to_add.items():
        old[k] = old[k] | v


def extract_matchIds(matchList):
    if "totalGames" in matchList and matchList["totalGames"] > 0:
        return [str(match["matchId"]) for match in matchList["matches"] if match["queue"] in allowed_queue_types]
    else:
        return[]


def extract_summonerIds(match):
    if "participantIdentities" not in match:
        print("'participantIdentities' missing in match!", file=sys.stderr)
        print(match, file=sys.stderr)
        return []
    return {pIdentity["player"]["summonerId"] for pIdentity in match["participantIdentities"]}

def getKeyOrMissing(dict, path, missingVal):
    try:
        return getFromDict(dict, path)
    except Exception as inst:
        return missingVal



def process_participant(participant, participantIdentity):
    return {
        "summonerId": str(participantIdentity["player"]["summonerId"]),
        "lane": participant["timeline"]["lane"],
        "role": participant["timeline"]["role"],
        "team": "blue" if (participant["teamId"] == 100) else "purple",
        "winner": participant["stats"]["winner"],
        "goldEarned": participant["stats"]["goldEarned"],
        "kills": participant["stats"]["kills"],
        "deaths": participant["stats"]["deaths"],
        "assists": participant["stats"]["assists"],
        "largestKillingSpree": participant["stats"]["largestKillingSpree"],
        "totalDamageDealt": participant["stats"]["totalDamageDealt"],
        "totalDamageDealtToChampions": participant["stats"]["totalDamageDealtToChampions"],
        "totalDamageTaken": participant["stats"]["totalDamageTaken"],
        "totalTimeCrowdControlDealt": participant["stats"]["totalTimeCrowdControlDealt"],

        # timeline stuff
        "csDiff10": getKeyOrMissing(participant, ["timeline", "csDiffPerMinDeltas", "zeroToTen"], 0),
        "cs10": getKeyOrMissing(participant, ["timeline", "creepsPerMinDeltas", "zeroToTen"], 3),
        "gpm10": getKeyOrMissing(participant, ["timeline", "goldPerMinDeltas", "zeroToTen"], 200),
        "xpDiff10": getKeyOrMissing(participant, ["timeline", "xpDiffPerMinDeltas", "zeroToTen"], 0),
        "csDiff20": getKeyOrMissing(participant, ["timeline", "csDiffPerMinDeltas", "tenToTwenty"], 0),
        "cs20": getKeyOrMissing(participant, ["timeline", "creepsPerMinDeltas", "tenToTwenty"], 6),
        "gpm20": getKeyOrMissing(participant, ["timeline", "goldPerMinDeltas", "tenToTwenty"], 400),
        "xpDiff20": getKeyOrMissing(participant, ["timeline", "xpDiffPerMinDeltas", "tenToTwenty"], 0)

        # "gpm20": participant["timeline"]["goldPerMinDeltas"]["tenToTwenty"],
        # "gpm30": participant["timeline"]["goldPerMinDeltas"]["twentyToThirty"],
        # "gpmToEnd": participant["timeline"]["goldPerMinDeltas"]["thirtyToEnd"]
        }


def process_match(match):
    if ("status" in match): # fix for 404
        return None

    return {
        "matchId": str(match["matchId"]),
        "region": match["region"],
        "queueType": match["queueType"],
        "matchDuration": match["matchDuration"],
        "participants": [process_participant(participant, participantIdentity) for (participant, participantIdentity) in zip(match["participants"], match["participantIdentities"])]
    }




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
        matches = {future_to_match[future]: process_match(future.result()) for future in concurrent.futures.as_completed(future_to_match)}

    return (player_matches, {match_id: match for match_id, match in matches.items() if match is not None})

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
