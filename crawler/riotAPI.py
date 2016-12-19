from collections import namedtuple
from rateController import RateController


RegionalEndpoint = namedtuple('RegionalEndpoint', ['region', 'platformId', 'host'])

WE_ENDPOINT = RegionalEndpoint('EUW', 'EUW1', 'euw.api.pvp.net')
EUNE_ENDPOINT = RegionalEndpoint('EUNE', 'EUN1', 'eune.api.pvp.net')


class RiotAPI:
    APIPaths = {
        'matchlist': '/api/lol/{region}/v2.2/matchlist/by-summoner/{summonerId}',
        'match': '/api/lol/{region}/v2.2/match/{matchId}',
        'featuredgames': '/observer-mode/rest/featured',
        'summoner': '/api/lol/{region}/v1.4/summoner/by-name/{summonerNames}',
    }
    URLs = {key: 'https://{host}' + val for key, val in APIPaths.items()}

    def __init__(self, regionalEndpoint, api_key, keyType):
        self.commonURLParams = \
            {key: val.lower() for key, val in regionalEndpoint._asdict().items()}
        self.api_key = api_key
        self.rateController = RateController(keyType)

    def formatURL(self, key, **kwargs):
        return self.URLs[key].format(**kwargs, **self.commonURLParams)
     
    def get(self, *args, **kwargs):
        ignoredStatusCodes = kwargs.get('ignored', [429, 500, 503])
        while True: 
            r = self.rateController.get(*args, **kwargs)
            if r.status_code not in ignoredStatusCodes:
                return r

    def matchlist(self, summonerId):
        url = self.formatURL('matchlist', summonerId=summonerId)
        r = self.get(url, params={'api_key': self.api_key})
        return r.json()

    def match(self, matchId):
        url = self.formatURL('match', matchId=matchId)
        r = self.get(url, params={'api_key': self.api_key, 'includeTimeline': 'false'})
        return r.json()

    def featuredgames(self):
        url = self.formatURL('featuredgames')
        r = self.get(url, params={'api_key': self.api_key})
        return r.json()

    def summoner(self, summonerNames):
        paramValue = ','.join(summonerNames)
        url = self.formatURL('summoner', summonerNames=paramValue)
        r = self.get(url, params={'api_key': self.api_key})
        return r.json()

