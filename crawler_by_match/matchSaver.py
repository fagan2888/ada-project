import csv


class MatchSaver:
    def __init__(self, f):
        self.csvWriter = csv.writer(f, delimiter=',', lineterminator='\n')

    def processParticipant(self, participant):
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

    def matchToList(self, o):
        fixed = [
          o['matchId'],
          o['matchDuration'],
          o['region'],
          o['queueType']
        ]
        participants = [item for p in o['participants'] for item in self.processParticipant(p)]

        return fixed + participants

    def saveMatches(self, matches):
        matches_arr = [self.matchToList(match) for match in matches]
        self.csvWriter.writerows(matches_arr)
