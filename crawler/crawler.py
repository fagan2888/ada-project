import sys
from itertools import chain


def get_random_summonerId(riotAPI):
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


def extract_summonerIds(match):
    if 'participantIdentities' not in match:
        print("'participantIdentities' missing in match!", file=sys.stderr)
        print(match, file=sys.stderr)
        return []
    return [pIdentity['player']['summonerId'] for pIdentity in match['participantIdentities']]


def crawl(riotAPI, matchesPerSummoner, summonersNum, startId=None):
    if startId is None:
        startId = get_random_summonerId(riotAPI)
    
    avaiableSummoners = set([startId])
    processedSummoners = {}
    matches = {}
    while len(processedSummoners) < summonersNum:
        summonerId = avaiableSummoners.pop()
        r = riotAPI.matchlist(summonerId)
        matchIds = extract_matchIds(r)[:matchesPerSummoner]
        processedSummoners[summonerId] = matchIds
        newMatches = [(mId, riotAPI.match(mId)) for mId in matchIds if mId not in matches]
        matches.update(dict(newMatches))
        summonerIds = chain.from_iterable(extract_summonerIds(m[1]) for m in newMatches)
        newSummonerIds = [sId for sId in summonerIds if sId not in processedSummoners]
        avaiableSummoners.update(set(newSummonerIds))

    return {
        'summoners': processedSummoners,
        'matches': matches,
    }
