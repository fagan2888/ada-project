# Features generation

This code uses the crawled matches information to generate the features fed to the neural network.

The order of the operations is:

* join the list of processed matches (the ones were we have the last n matches of all players) with the match information to get the summoner id and generate the position of the player. This gives the participants
* Flatten the participants (wide to long)
* Join with the list of matches of the players
* Flatten that list
* Join with the match info
* Group by match id, summoner id and team and apply the feature generation function
* Save those features (for the statistics)
* reshape from long to wide to get the features of one match in a row and save (for the neural network)
