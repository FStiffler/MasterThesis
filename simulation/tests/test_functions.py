from unittest import TestCase
import pandas as pd
import itertools as it
from functions import solve_ranking_conflicts
from functions import simulate_game


class Test(TestCase):
    def test_solve_ranking_conflicts(self):
        """
            Description:
            Unit test for solve_ranking_conflicts to see what happens when three equally strong teams with balanced records need to be placed

            Expected Outcome:
            All three teams can not be placed based on record and they have to play games against each other until there is
            a definitive ranking. Before that is the case, the function solve_ranking_conflicts should not return a result.
            """
        # create equal teams
        equalTeams = ['team' + str(i + 1) for i in range(3)]

        # assign equal skill level to each team
        skillDictionary = {team: 13 for team in equalTeams}

        # create pairings
        pairings = list(it.combinations(equalTeams, 2))

        # create empty record
        record = pd.DataFrame({'homeTeam': [], 'awayTeam': [], 'winner': []})

        # create predefined ranking
        ranking = pd.DataFrame({'rank': [0] * len(equalTeams),
                                'team': equalTeams,
                                'wins': 4})

        # for each pairing
        for pairing in pairings:
            # extract names of both teams
            homeTeam = pairing[0]
            awayTeam = pairing[1]

            # create game count
            game = 1

            # iterate over games
            while game < 5:

                # in the first two games
                if game < 3:

                    # the home team of pairing wins
                    newRecord = pd.DataFrame(
                        {'homeTeam': [homeTeam], 'awayTeam': [awayTeam], 'winner': [homeTeam]})
                    record = pd.concat([record, newRecord], ignore_index=True)

                    game += 1

                # in the second two games
                elif game > 2:

                    # the home team of pairing wins
                    newRecord = pd.DataFrame(
                        {'homeTeam': [homeTeam], 'awayTeam': [awayTeam], 'winner': [awayTeam]})
                    record = pd.concat([record, newRecord], ignore_index=True)

                    game += 1

        # put situation to test
        resolvedRanking = solve_ranking_conflicts(ranking, record, skillDictionary)

        # assert that each team has a unique rank after that
        assert len(set(resolvedRanking['rank'])) == 3

    def test_balanced_placement_games(self):
        """
            Description:
            Unit to see what happens when placement games lead to equal results and another round of placement games
            needs to be played

            Expected Outcome:
            Repeated replacement games
            """
        # create equal teams
        equalTeams = ['team' + str(i + 1) for i in range(3)]

        # assign equal skill level to each team
        skillDictionary = {team: 13 for team in equalTeams}

        # create pairings
        pairings = list(it.combinations(equalTeams, 2))

        # create empty record
        record = pd.DataFrame({'homeTeam': [], 'awayTeam': [], 'winner': []})

        # create predefined ranking
        ranking = pd.DataFrame({'rank': [0] * len(equalTeams),
                                'team': equalTeams,
                                'wins': 4})

        # create predefined record
        for pairing in pairings:
            # extract names of both teams
            homeTeam = pairing[0]
            awayTeam = pairing[1]

            # create game count
            game = 1

            # iterate over games
            while game < 5:

                # in the first two games
                if game < 3:

                    # the home team of pairing wins
                    newRecord = pd.DataFrame(
                        {'homeTeam': [homeTeam], 'awayTeam': [awayTeam], 'winner': [homeTeam]})
                    record = pd.concat([record, newRecord], ignore_index=True)

                    game += 1

                # in the second two games
                elif game > 2:

                    # the home team of pairing wins
                    newRecord = pd.DataFrame(
                        {'homeTeam': [homeTeam], 'awayTeam': [awayTeam], 'winner': [awayTeam]})
                    record = pd.concat([record, newRecord], ignore_index=True)

                    game += 1

        # initialise placement decision status
        placementDecision = False

        # while no decision
        while not placementDecision:

            # initialise empty ranking
            placementRanking = pd.DataFrame({'rank': [0] * len(equalTeams),
                                             'team': equalTeams,
                                             'wins': [0] * len(equalTeams)
                                             })

            # initialise record of all game outcomes
            placementGamesRecord = pd.DataFrame({'homeTeam': [], 'awayTeam': [], 'winner': []})

            # create each possible team pairing for regular season
            placementPairings = list(it.combinations(equalTeams, 2))

            # for each pairing
            for pairing in placementPairings:
                # extract skills of both teams
                homeTeam = pairing[0]
                awayTeam = pairing[1]
                skillFirstTeam = skillDictionary[homeTeam]
                skillSecondTeam = skillDictionary[awayTeam]

                # simulate game between team pairing
                winner = simulate_game(homeTeam, skillFirstTeam, awayTeam, skillSecondTeam)

                # add a win to the winning team's record
                placementRanking.loc[placementRanking['team'] == winner, 'wins'] += 1

                # sort ranking
                placementRanking.sort_values('wins', ignore_index=True, inplace=True, ascending=False)

                # newPlacementRecord
                newRecord = pd.DataFrame(
                    {'homeTeam': [homeTeam], 'awayTeam': [awayTeam], 'winner': [winner]})

                # concat new record with record of previous games
                placementGamesRecord = pd.concat([placementGamesRecord, newRecord], ignore_index=True)

            # recursively call solve_ranking_conflicts but with predefined ranking and record
            finalPlacementRanking = solve_ranking_conflicts(ranking, record, skillDictionary)

            # if ranking is resolved
            placementDecision = True

            # assertion
            assert len(set(finalPlacementRanking['rank'].tolist())) == len(equalTeams)
