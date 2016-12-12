import requests
from rateController import RateController
from decorators import rateControlled, ignoreStatusCodes
import json
import itertools


with open('api_key.txt') as f:
    API_KEY = f.read()


# REGIONAL ENDPOINT FOR WEST EUROPE
region = 'EUW'
platformID = 'EUW1'
host = 'euw.api.pvp.net'

# The only player we know: Moegami
startID = 20391818


def matchlistURL(summonerId):
    matchlistPath = '/api/lol/{region}/v2.2/matchlist/by-summoner/{summonerId}'
    return 'https://' + host + matchlistPath.format(region=region, summonerId=summonerId)


def matchURL(matchId):
    matchPath = '/api/lol/{region}/v2.2/match/{matchId}'
    return 'https://' + host + matchPath.format(region=region, matchId=matchId)

rateController = RateController()

@ignoreStatusCodes([429, 503])
@rateControlled(rateController)
def get_matchlist(summonerId):
    r = requests.get(matchlistURL(startID), params={'api_key': API_KEY})
    return r


@ignoreStatusCodes([429, 503])
@rateControlled(rateController)
def get_match(matchId):
    r = requests.get(matchURL(matchId), params={'api_key': API_KEY})
    return r


def extract_matchIds(matchList):
    return [match['matchId'] for match in matchList['matches']]


def extract_participantIds(match):
    return [participant['participantId'] for participant in match['participants']]


def BFS(startID, matchesPerSummoner, summonersNum):
    avaiableSummoners = set([startID])
    processedSummoners = {}
    matches = {}
    while len(processedSummoners) < summonersNum:
        summoner = avaiableSummoners.pop()
        r = get_matchlist(summoner)
        matchIds = extract_matchIds(r.json())[:matchesPerSummoner]
        processedSummoners[summoner] = matchIds
        newMatchIds = [matchId for matchId in matchIds if matchId not in matches]
        newMatches = [get_match(matchId).json() for matchId in matchIds]
        matches.update(dict(zip(newMatchIds, newMatches)))
        participantIds = list(itertools.chain(*[extract_participantIds(match) for match in newMatches]))
        newSummoners = [participantId for participantId in participantIds if participantId not in processedSummoners]
        avaiableSummoners.update(set(newSummoners))

    return {
        'avaiableSummoners': list(avaiableSummoners),
        'summoners': processedSummoners,
        'matches': matches,
    }

def print_response(r):
    print(r)
    print (r.url)
    print(r.headers)

def test_stupid():
    for i in range(600):
        r = get_matchlist(startID)
    

if __name__ == '__main__':
    result = BFS(startID, 5, 5)
    print(json.dumps(result))
