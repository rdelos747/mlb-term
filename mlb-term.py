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
    #print (res['dates'][0])

    for g in res['dates'][0]['games']:
        if g['status']['abstractGameState'] == 'Live':
            pk = g['gamePk']
            home = g['teams']['home']['team']
            away = g['teams']['away']['team']
            print(str(pk) + ' ' + away['name'] + ' @ ' + home['name'])


def game(ver, gamePk):
    url = BASE + str(ver) + '/game/' + str(gamePk) + '/feed/live'

    '''
    all data
    '''
    data = requests.get(url)
    res = data.json()

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
    all_plays = res['liveData']['plays']['allPlays']
    cur_play_idx = len(all_plays) - 1
    result = all_plays[cur_play_idx]['result']
    #print(result)

    about = all_plays[cur_play_idx]['about']

    half = about['halfInning']
    #print(' ')

    print(list(res['liveData'].keys()))
    print(res['liveData']['linescore'])
    print(' ')

     #print title
    print(f'{away_name}({away_win}-{away_loss}) @ {home_name}({home_win}-{home_loss})')

    away_score = away_abv + ' '
    home_score = home_abv + ' '
    for i in range(9):
        away_score += '--- '
        home_score += '--- '

    print(f'{away_score}')
    print(f'{home_score}')

    desc = None
    if 'description' in result:
        desc = result['description']
    print(desc)


def run():
    schedule('v1')
    print(' ')
    game('v1.1', 777718)


if __name__ == '__main__':
    run()
