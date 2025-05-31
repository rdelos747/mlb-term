#import console
import requests
import json

BASE = 'https://statsapi.mlb.com/api/'

def schedule(ver):
    url = BASE + str(ver) + '/schedule/?sportId=1'

    res = requests.get(url).json()
    #print(res.json())
    #for r in (res):
    #print(res['dates'])
    #print (res['dates'][0]['games'])

    for g in res['dates'][0]['games']:
        if g['status']['abstractGameState'] == 'Live':
            #print (g)
            pk = g['gamePk']

            away = g['teams']['away']
            away_name = away['team']['name']
            away_score = away['score']
            away_win = away['leagueRecord']['wins']
            away_loss = away['leagueRecord']['losses']
            away_pct = away['leagueRecord']['pct']

            home = g['teams']['home']
            home_name = home['team']['name']
            home_score = home['score']
            home_win = home['leagueRecord']['wins']
            home_loss = home['leagueRecord']['losses']
            home_pct = home['leagueRecord']['pct']

            #print(str(pk) + ' ' + away_name + ' @ ' + home_name)
            print(f'{pk} {away_name}({away_win}-{away_loss})[{away_score}] @ {home_name}({home_win}-{home_loss})[{home_score}]')


def game(ver, gamePk):
    url = BASE + str(ver) + '/game/' + str(gamePk) + '/feed/live'

    '''
    all data
    '''
    data = requests.get(url)
    res = data.json()
    all_plays = res['liveData']['plays']['allPlays']
    cur_play_idx = len(all_plays) - 1
    about = all_plays[cur_play_idx]['about']
    line_score = res['liveData']['linescore']

    '''
    game data
    '''
    game_data = res['gameData']
    away = game_data['teams']['away']
    home = game_data['teams']['home']

    away_name = away['name']
    away_abv = away['abbreviation']
    away_win = away['record']['wins']
    away_loss = away['record']['losses']
    away_perc = away['record']['winningPercentage']

    home_name = home['name']
    home_abv = home['abbreviation']
    home_win = home['record']['wins']
    home_loss = home['record']['losses']
    home_perc = home['record']['winningPercentage']

    '''
    live data
    '''

    #print(result)



    #print(about)
    half = about['halfInning']
    current_inning = about['inning']
    current_inning_ord = line_score['currentInningOrdinal']
    #print(' ')

    print(list(res['liveData'].keys()))
    #print(res['liveData']['linescore'])
    print(' ')

     #print title
    print(f'{away_name}({away_win}-{away_loss}) @ {home_name}({home_win}-{home_loss}) -- {half} {current_inning_ord}')

    #away_score = away_abv + ' '
    #ome_score = home_abv + ' '

    side_scores = [
        away_abv,
        home_abv
    ]
    if half == 'Top':
        side_scores[0] += '* '
        side_scores[1] += '  '
    else:
        side_scores[0] += '  '
        side_scores[1] += '* '

    for i in range(current_inning):
        #away_run = '-'
        #away_hit = '-'
        #away_err = '-'
        for s in range(len(side_scores)):
            side = s == 0 and 'away' or 'home'
            for key in ['runs', 'hits', 'errors']:
                if key in line_score['innings'][i][side]:
                    scr = line_score['innings'][i][side][key]
                    if scr != 0:
                        side_scores[s] += str(scr) +''
                    else:
                        side_scores[s] += '-'
                else:
                    side_scores[s] += '-'
            side_scores[s] += ' '

    for _ in range(9 - current_inning):
        for i in range(len(side_scores)):
            side_scores[i] += '--- '

    side_scores[0] += '| '
    side_scores[1] += '| '

    for s in range(len(side_scores)):
        side = s == 0 and 'away' or 'home'
        for key in ['runs', 'hits', 'errors']:
            if key in line_score['teams'][side]:
                scr = line_score['teams'][side][key]
                if scr != 0:
                    side_scores[s] += str(scr)
                    if scr < 10:
                        side_scores[s] += ' '
                else:
                    side_scores[s] += '- '
            else:
                side_scores[s] += '- '



    print(f'{side_scores[0]}')
    print(f'{side_scores[1]}')
    #print(f'{home_score}')

    count = all_plays[cur_play_idx]['count']
    match = all_plays[cur_play_idx]['matchup']
    #count_balls =
    #count_strikes = count['strikes']
    #count_outs = count['outs']

    count_row = f'{half} {current_inning_ord} '
    count_row += 'O:'
    for i in range(2):
        if i < count['outs']:
            count_row += 'X'
        else:
            count_row += '_'

    count_row += f' {count['balls']}-{count['strikes']} < '
    count_row += f'{match['batter']['fullName']}({match['batSide']['code']})'

    pitches = all_plays[cur_play_idx]['playEvents']
    '''
    print(pitches)
    for i in range(len(pitches) - 1, len(pitches) - 5,-1):
        print(i)
        count_row += pitches[i]['details']['description']
    '''

    print(count_row)

    pitch_row = f'{match['pitcher']['fullName']}({match['pitchHand']['code']})'
    print(pitch_row)

    #result = all_plays[cur_play_idx]['result']

    descs = []
    desc_idx = cur_play_idx
    while len(descs) < 5 and desc_idx >= 0:
        result = all_plays[desc_idx]['result']
    #desc = None
        if 'description' in result:
            #desc = result['description']
            descs.append(all_plays[desc_idx]['result']['description'])
        desc_idx -= 1

        '''
            Consider also looping through each plays ['playEvents'] for interesting
            events. Eg anything with a description longer than N characters can be
            added to this list
        '''
    for d in reversed(descs):
        print(d)


def run():
    schedule('v1')
    print(' ')
    game('v1.1', 777708)


if __name__ == '__main__':
    run()
