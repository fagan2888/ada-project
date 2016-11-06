##Abstract
  This project will crawl publicly available League of Legends match information obtained using the riot api, apply a 2-step process of extracting player features and feeding them to a neural network that will be used to predict the winning chance of a new match based on the players previous results and team composition.
  The features retained during the tuning of the model will be made available and visualized on a player page to show relevant information.

##Plan
  * Crawl the data from the api:
    * previous matches information
    * current division of the players (and historical if available)
  
  * store the result of the api queries
  * process it:
    for each player we use the info of their previous matches to generate features for every match observation (using only information available at the time the match was played, so for example for match 10 we will only use info from match 1 to 9)

  * Train a neural network that is fed the historical features of the present players predicting which team will win

##Data Description
  To sumarize, we will keep aggregated information (at the match level) on player performance, role played, identity of the players and final result for each of their played games.
  This data will later be grouped by player and used to generate the features.

  https://developer.riotgames.com/api/methods#!/1064/3671
  basic information retained:
    matchid (used to sort games by time)
    matchType we only retain MATCHED_GAME
    matchMode we only retain CLASSIC
    queueType
    region
    participantIdentities
    participants (KDA, firstBlood info, GPM, warding info, winner)

##Feasibility and Risks
  The large quantity of data available makes both the crawling and processing a challenge. However, we can simply base the analysis on a subset (only one region) if we cannot manage to process everything. A further complication of the riot api is the rate limitation (360k queries per hour), which will force us to setup a continuous ingestion system.
  Another challenge is identifying  features that are relevant to the prediction. This will be the most time consuming part and will mostly rely on the knowledge of the game of one of the team members.




##deliverable:
  viz of some features (scoring singular players, aggregated statistics per role, distribution of main role played by ranking)
  predicting platform that takes the id (name and region) and role of the present players and returns the winning chance of each side

##Timeplan:
  mid-november:
    Get accustomed the match api and have a basic query system working

  early december:
    Have a continuous crawling system allowing us to get offline data (at least last 3 months of data for a region)
    Initial features generating system + prediction system

  mid-december:
    Tune the features to improve the prediction accuracy

  end of december:
    Build an online prediction system that takes the players + roles in the match and returns the winning chances

  january:
    create an online viz of the features identified during the tuning (by player)
    create a viz of the evolution of the champion features (wrt time)

