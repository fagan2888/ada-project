from crawler import get_last_matches
from riotAPI import RiotAPI, EUW_ENDPOINT

import pandas as pd


def init_API():
  with open('api_key.txt') as f:
      API_KEY = f.read().strip()

  riotAPI = RiotAPI(EUW_ENDPOINT, API_KEY, 'production')

  return riotAPI

def get_id(name, riotAPI):
  res = riotAPI.summoner([name])
  if ('status' in res and 'status_code' in res['status']): # user not found
    return ''
  else:
    return str(res[name.replace(" ", "")]['id'])

def get_features(summs, riotAPI):
  matchesPerSummoner = 20

  player_matches, last_matches = get_last_matches(summs, {}.keys(), riotAPI, matchesPerSummoner)

  return gen_features(summs, player_matches, last_matches)

def gen_features(summs, player_matches, last_matches):
  summs_idx = [{'summ_id': summ, 'player_num': idx} for idx, summ in enumerate(summs)]
  df_summs = pd.DataFrame(summs_idx)

  df_matches = pd.DataFrame.from_dict(last_matches, orient='index')

  player_matches_unnested = [{"summ_id": key, "match_id": item} for key, items in player_matches.items() for item in items]
  df_player_matches = pd.DataFrame(player_matches_unnested)

  def gen_player_features(matches):
      summId = matches.ix[0]['summ_id']
      player_num = matches.ix[0]['player_num']

      def getInfo(match):
          return pd.Series([info for info in match['participants'] if info['summonerId'] == summId][0])

      infos = matches.apply(getInfo, axis = 1)


      totalGames = max(len(matches.index), 1)

      # winrate
      winrate = infos['winner'].sum() / totalGames

      # GPM
      GPM = 60.0 * infos['goldEarned'].sum() / matches['matchDuration'].sum()

      # KDA
      kills = infos['kills'].sum()
      assists = infos['assists'].sum()
      deaths = infos['deaths'].sum()

      KDA = (kills+deaths) / max(deaths, 1)
      KD = kills / max(deaths, 1)

      largestKillingSpree = infos['largestKillingSpree'].mean()

      totalDamageDealt = infos['totalDamageDealt'].mean()

      totalDamageDealtToChampions = infos['totalDamageDealtToChampions'].mean()

      totalDamageTaken = infos['totalDamageTaken'].mean()

      totalTimeCrowdControlDealt = infos['totalTimeCrowdControlDealt'].mean()

      # timeline stuff

      cs10 = infos['cs10'].mean()
      cs20 = infos['cs20'].mean()

      csDiff10 = infos['csDiff10'].mean()
      csDiff20 = infos['csDiff20'].mean()

      gpm10 = infos['gpm10'].mean()
      gpm20 = infos['gpm20'].mean()

      xpDiff10 = infos['xpDiff10'].mean()
      xpDiff20 = infos['xpDiff20'].mean()

      return pd.Series({
  #             'summ_id': summId,
              'player_num': player_num,
              'winrate': winrate,
              'GPM': GPM,
              'KDA': KDA,
              'KD': KD,
              'largestKillingSpree': largestKillingSpree,
              'totalDamageDealt': totalDamageDealt,
              'totalDamageDealtToChampions': totalDamageDealtToChampions,
              'totalDamageTaken': totalDamageTaken,
              'totalTimeCrowdControlDealt': totalTimeCrowdControlDealt,
              'cs10': cs10,
              'cs20': cs20,
              'csDiff10': csDiff10,
              'csDiff20': csDiff20,
              'gpm10': gpm10,
              'gpm20': gpm20,
              'xpDiff10': xpDiff10,
              'xpDiff20': xpDiff20
          })


  df_features = pd.merge(df_summs, df_player_matches, left_on = 'summ_id', right_on = 'summ_id').set_index('match_id').join(df_matches).groupby(['summ_id', 'player_num']).apply(gen_player_features)
  df_features = df_features.ix[:, ["player_num", "winrate", "GPM", "KDA", "KD", "largestKillingSpree", "totalDamageDealt",
          "totalDamageDealtToChampions", "totalDamageTaken","totalTimeCrowdControlDealt",
          "cs10", "cs20", "csDiff10", "csDiff20", "gpm10", "gpm20", "xpDiff10", "xpDiff20"]].set_index(['player_num'])

  features = df_features.values.tolist()


  return [[feature for sublist in features for feature in sublist]]
