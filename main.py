import sys
import urllib.request
import json
from pprint import pprint
import datetime

# probably rewrite this to take a command line argument or something
club_id = "club-name-here"  # the end of the URL on the club page, ex. https://www.chess.com/club/club-name-here

if __name__ == "__main__":
    print(f"\ngetting club data for {club_id}...", end="")
    club_name = urllib.request.urlopen(f"https://api.chess.com/pub/club/{club_id}")
    if club_name.status != 200:
        print(f"\n\tHTTP error code f{club_name.status} received. Exiting")
        sys.exit()
    print("done")
    club_name_json = json.loads(club_name.read())
    clubfullname = club_name_json['name']

    club_contents = urllib.request.urlopen(f"https://api.chess.com/pub/club/{club_id}/members")
    if club_contents.status != 200:
        print(f"\n\tHTTP error code f{club_contents.status} received. Exiting")
        sys.exit()
    print("done")

    club_json = json.loads(club_contents.read())
    
    members = club_json["weekly"]
    members += club_json["monthly"]
    members += club_json["all_time"]

    puzzle_scores = []
    daily_scores_current = []
    daily_scores_alltime = []
    rapid_scores_current = []
    rapid_scores_alltime = []
    
    for member in members:
        # get the data from chess dot com
        print(f"\tgetting data for {member['username']}...", end="")
        member_metadata = urllib.request.urlopen(f"https://api.chess.com/pub/player/{member['username']}")
        if member_metadata.status != 200:
            print(f"\n\t\tHTTP error code f{member_metadata.status} received. Exiting")
            sys.exit()

        member_stats = urllib.request.urlopen(f"https://api.chess.com/pub/player/{member['username']}/stats")
        if member_stats.status != 200:
            print(f"\n\t\tHTTP error code f{member_stats.status} received. Exiting")
            sys.exit()
        print('done')
        

        # extract the stats I want and store in the appropriate list (puzzle_scores, daily_scores_current, etc.)
        # this needs to be a bit more robust to handle all cases where a user doesnt have a daily/puzzle/rapid/other rating
        member_json = json.loads(member_metadata.read())
        username = member_json['url'].split('/')[-1]

        stats_json = json.loads(member_stats.read())

        puzzlescore = stats_json['tactics']['highest']['rating']
        bestdate = stats_json['tactics']['highest']['date']
        puzzle_scores.append({'name':username, 'score':puzzlescore, 'date':datetime.datetime.utcfromtimestamp(bestdate)})

        if stats_json.get('chess_daily', None):
            score = stats_json['chess_daily']['last']['rating']
            sdate = stats_json['chess_daily']['last']['date']
            daily_scores_current.append({'name':username, 'score':score, 'date':datetime.datetime.utcfromtimestamp(sdate)})

            record = stats_json['chess_daily']['record']
            score = stats_json['chess_daily'].get('best', {'rating':None})['rating']
            sdate = stats_json['chess_daily'].get('best', {'date':None})['date']
            if score:
                daily_scores_alltime.append({'name':username, 'score':score, 'date':datetime.datetime.utcfromtimestamp(sdate), 'record': record})

        if stats_json.get('chess_rapid', None):
            score = stats_json['chess_rapid'].get('last', {'rating': None})['rating']
            sdate = stats_json['chess_rapid']['last']['date']
            if score:
                rapid_scores_current.append({'name':username, 'score':score, 'date':datetime.datetime.utcfromtimestamp(sdate)})

            record = stats_json['chess_rapid']['record']
            score = stats_json['chess_rapid'].get('best', {'rating': None})['rating']
            sdate = stats_json['chess_rapid']['best']['date']
            if score:
                rapid_scores_alltime.append({'name':username, 'score':score, 'date':datetime.datetime.utcfromtimestamp(sdate), 'record': record})



    # we have scores for all members, now sort in order of score and display
    puzzle_scores = sorted(puzzle_scores, key = lambda x: x['score'], reverse=True)
    print("\n\n")
    print(f"~~~ {clubfullname} All Time Puzzle Leaderboard ~~~")
    for ii, score in enumerate(puzzle_scores):
        print(f"{ii+1:2d}. {score['name']:16s} - {score['score']:4d} on {score['date'].strftime('%Y-%m-%d')}")
    print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~{'~'*len(clubfullname)}\n\n\n")

    daily_scores_current = sorted(daily_scores_current, key = lambda x: x['score'], reverse=True)
    print(f"~~~ {clubfullname} Daily Correspondence Leaderboard ~~~")
    for ii, score in enumerate(daily_scores_current):
        print(f"{ii+1:2d}. {score['name']:16s} - {score['score']:4d}")
    print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~{'~'*len(clubfullname)}\n\n\n")

    rapid_scores_current = sorted(rapid_scores_current, key = lambda x: x['score'], reverse=True)
    print(f"~~~ {clubfullname} Rapid Leaderboard ~~~")
    for ii, score in enumerate(rapid_scores_current):
        print(f"{ii+1:2d}. {score['name']:16s} - {score['score']:4d}")
    print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~{'~'*len(clubfullname)}\n\n\n")

    daily_scores_alltime = sorted(daily_scores_alltime, key = lambda x: x['score'], reverse=True)
    print(f"~~~ {clubfullname} Daily Correspondence All-Time Leaderboard ~~~")
    for ii, score in enumerate(daily_scores_alltime):
        print(f"{ii+1:2d}. {score['name']:16s} - {score['score']:4d} on {score['date'].strftime('%Y-%m-%d')} ({score['record']['win']}W/{score['record']['loss']}L/{score['record']['draw']}D)")
    print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~{'~'*len(clubfullname)}\n\n\n")

    rapid_scores_alltime = sorted(rapid_scores_alltime, key = lambda x: x['score'], reverse=True)
    print(f"~~~ {clubfullname} Rapid All-Time Leaderboard ~~~")
    for ii, score in enumerate(rapid_scores_alltime):
        print(f"{ii+1:2d}. {score['name']:16s} - {score['score']:4d} on {score['date'].strftime('%Y-%m-%d')} ({score['record']['win']}W/{score['record']['loss']}L/{score['record']['draw']}D)")
    print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~{'~'*len(clubfullname)}\n\n\n")