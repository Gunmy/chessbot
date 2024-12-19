def filter_games_with_evaluations(input_file, output_file):
    """
    Filters games out games without evaluations

    Args:
        input_file (str): Path to the input .pgn file.
        output_file (str): Path to save the filtered games with evaluations.
    """
    with open(input_file, 'r', encoding='utf-8') as infile:
        games = infile.read().split('\n')

    games_with_evaluations = [
        game for game in games if '[%eval' in game
    ]

    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write('\n'.join(games_with_evaluations))
        print(f"Filtered {len(games_with_evaluations)} games with evaluations out of {len(games)} total games.")

filter_games_with_evaluations('lichess_db_standard_rated_2015-08.pgn', 'filtered_games.pgn')