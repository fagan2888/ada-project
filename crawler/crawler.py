import json
from itertools import chain
from riotAPI import RiotAPI, EUNE_ENDPOINT


MoegamiID = 20391818

with open('api_key.txt') as f:
    API_KEY = f.read().strip()

riotAPI = RiotAPI(EUNE_ENDPOINT, API_KEY)


def get_random_summonerId():
    r = riotAPI.featuredgames()
    participants = chain.from_iterable(x['participants'] for x in r['gameList'])
    summonerNames = [x['summonerName'] for x in participants if not x['bot']]
    r2 = riotAPI.summoner(summonerNames[:1])
    return [summonerDto['id'] for summonerDto in r2.values()][0]


def extract_matchIds(matchList):
    if matchList['totalGames'] > 0:
        return [match['matchId'] for match in matchList['matches']]
    else:
        return[]


def extract_participantIds(match):
    return [pIdentity['player']['summonerId'] for pIdentity in match['participantIdentities']]


def BFS(matchesPerSummoner, summonersNum, startID=None):
    if startID is None:
        startID = get_random_summonerId()
    
    avaiableSummoners = set([startID])
    processedSummoners = {}
    matches = {}
    while len(processedSummoners) < summonersNum:
        summoner = avaiableSummoners.pop()
        r = riotAPI.matchlist(summoner)
        matchIds = extract_matchIds(r)[:matchesPerSummoner]
        processedSummoners[summoner] = matchIds
        newMatchIds = [matchId for matchId in matchIds if matchId not in matches]
        newMatches = [riotAPI.match(matchId) for matchId in matchIds]
        matches.update(dict(zip(newMatchIds, newMatches)))
        participantIds = chain.from_iterable(extract_participantIds(match) for match in newMatches)
        newSummoners = [participantId for participantId in participantIds if participantId not in processedSummoners]
        avaiableSummoners.update(set(newSummoners))

    return {
        'summoners': processedSummoners,
        'matches': matches,
    }


if __name__ == '__main__':
    result = BFS(5, 5)
    print(json.dumps(result))
