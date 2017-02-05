# This code crawls League of Legends data using Riot API.

In order to train a neural network we need full data about thousands (*m*) of matches.

Full data about a match involves:
1. The match statistics.
2. Statistics of each of the last *n* matches of every participant.

The crawler offers a command line interface which allows to specify *n* and *m* as well as other options.
Most of the data is continously saved to disk thus preventing memory shortage.
