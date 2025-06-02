#import console
import argparse
import curses
import json
import os
import requests
import shutil
import sys
import time

from utils import *

BASE = 'https://statsapi.mlb.com/api/'

TERM_W = -1
SCROLL_W = 60

def schedule(ver):
    url = BASE + str(ver) + '/schedule/?sportId=1'

    res = requests.get(url).json()
    #print(res.json())
    #for r in (res):
    #print(res['dates'])
    #print (res['dates'][0]['games'])

    for g in res['dates'][0]['games']:
        #if g['status']['abstractGameState'] == 'Live':
            #print (g)
        pk = g['gamePk']
        status = g['status']['abstractGameState']

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
        print(f'{pk} <{status}> [{away_score}-{home_score}] {away_name}({away_win}-{away_loss}) @ {home_name}({home_win}-{home_loss})')


def get_live_data(ver, gamePk):
    '''
    Row data:
    00: title row
    01: away line score
    02: home line score
    03: count
    04: pitcher
    05: batters
    06: history -5
    07: history -4
    08: history -3
    09: history -2
    10: history -1
    '''
    rows = [{'scroll_idx':0, 'scroll_time':time.time(), 'text':''} for _ in range(11)]

    '''
    all data
    '''
    url = BASE + str(ver) + '/game/' + str(gamePk) + '/feed/live'
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

    #print(list(res['liveData'].keys()))
    #print(list(res['liveData']['boxscore'].keys()))
    #print(res['liveData']['linescore'])
    print(' ')
    #print(list(res['gameData'].keys()))

    #print(' ')
    #print(list(res['liveData']['plays'].keys()))
    #print(res['liveData']['plays']['currentPlay'])
    #print(' ')

     #print title
    #print(f'{away_name}({away_win}-{away_loss}) @ {home_name}({home_win}-{home_loss}) -- {half} {current_inning_ord}')
    title = f'{away_name}({away_win}-{away_loss}) @ {home_name}({home_win}-{home_loss})'

    #away_score = away_abv + ' '
    #ome_score = home_abv + ' '

    side_scores = [
        away_abv,
        home_abv
    ]
    for i in range(len(side_scores)):
        if len(side_scores[i]) < 3:
            side_scores[i] += ' '

    if half == 'Top':
        side_scores[0] += '* '
        side_scores[1] += '  '
    else:
        side_scores[0] += '  '
        side_scores[1] += '* '

    for i in range(current_inning):
        vals=[]
        for key in ['runs', 'hits', 'errors']:
            val = [0,0]
            for s in range(len(side_scores)):
                side = s == 0 and 'away' or 'home'
                if key in line_score['innings'][i][side]:
                    val[s] = line_score['innings'][i][side][key]
            vals.append(val)

        for v in vals:
            if v[0] > 9 and v[1] < 10:
                v[1] = str(v[1]) + ' '
            elif v[1] > 9 and v[1] < 10:
                v[0] = str(v[0]) + ' '
            side_scores[0] += str(v[0])
            side_scores[1] += str(v[1])
        side_scores[0] += ' '
        side_scores[1] += ' '

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



    #print(f'{side_scores[0]}')
    #print(f'{side_scores[1]}')
    #print(f'{home_score}')

    count = all_plays[cur_play_idx]['count']
    match = all_plays[cur_play_idx]['matchup']

    #test = requests.get('https://statsapi.mlb.com/' + match['pitcher']['link']).json()
    #print(test)
    #count_balls =
    #count_strikes = count['strikes']
    #count_outs = count['outs']

    count_row = f'{format_half(half)} {current_inning_ord} '
    count_row += 'O:'
    for i in range(2):
        if i < count['outs']:
            count_row += 'X'
        else:
            count_row += '_'
    count_row += f' {count['balls']}-{count['strikes']}'

    pitches = all_plays[cur_play_idx]['playEvents']
    pitch_row = f'{match['pitchHand']['code']}hp {match['pitcher']['fullName']}'

    bat_row = f'{match['batter']['fullName']}({match['batSide']['code']})'

    #print(pitches)
    if len(pitches) > 0:
        if 'call' in pitches[len(pitches) - 1]['details']:
            bat_row += f' p{len(pitches)} {pitches[len(pitches)-1]['details']['call']['description']}'

        if 'type' in pitches[len(pitches) - 1]['details']:
            pitch_row += f' {pitches[len(pitches) - 1]['pitchData']['startSpeed']}mph'
            pitch_row += f' {pitches[len(pitches) - 1]['details']['type']['description']}'

    '''
    print(pitches)
    for i in range(len(pitches) - 1, len(pitches) - 5,-1):
        print(i)
        count_row += pitches[i]['details']['description']
    '''

    bat_row += f' << {line_score['offense']['onDeck']['fullName']}'

    #print(count_row)
    #print(pitch_row)

    #result = all_plays[cur_play_idx]['result']

    descs = []
    play_idx = cur_play_idx
    while len(descs) < 5 and play_idx >= 0:
        result = all_plays[play_idx]['result']
        cur_half = format_half(all_plays[play_idx]['about']['halfInning'])
        cur_inning = all_plays[play_idx]['about']['inning']

        if 'description' in result:
            #desc = result['description']
            descs.append(f'-{len(descs) + 1} {cur_half}-{cur_inning} {all_plays[play_idx]['result']['description']}')

        pitches = all_plays[play_idx]['playEvents']
        for p in pitches:
            if len(descs) < 5 and 'description' in p['details'] and len(p['details']['description']) > 15:
                descs.append(f'-{len(descs) + 1} {cur_half}-{cur_inning} {p['details']['description']}')


        play_idx -= 1

        '''
            Consider also looping through each plays ['playEvents'] for interesting
            events. Eg anything with a description longer than N characters can be
            added to this list
        '''
    descs = list(reversed(descs))
    #d in reversed(descs):
        #print(d)

    rows[0]['text'] += title
    rows[1]['text'] += side_scores[0]
    rows[2]['text'] += side_scores[1]
    rows[3]['text'] += count_row
    rows[4]['text'] += pitch_row
    rows[5]['text'] += bat_row
    for i in range(6, 11):
        if i - 6 < len(descs):
            rows[i]['text'] += descs[i - 6]

    return {'rows':rows}



def print_game(data):
    #print(data)
    for r in data['rows']:
        #if len(r['text']) > 10:
        #    r['scroll_idx'] += 1
        t = r['text'][r['scroll_idx']:SCROLL_W]
        print(t)

def scroll_game(data):
    for r in data['rows']:
        cur_time = time.time()
        #if cur_time - r['scroll_time'] > 1 and
        #if len(r['text']) > SCROLL_W:
        #print(r['scroll_time'])
        if cur_time - r['scroll_time'] > 1:
            if r['scroll_idx'] < len(r['text']) - SCROLL_W:
                r['scroll_idx'] += 1
                #if r['scroll_idx'] > len(r['text']) - SCROLL_W:
                #    r['scroll_idx'] = 0
                t = r['text'][r['scroll_idx']:SCROLL_W+r['scroll_idx']]
                print(t, end = '\r')
            else:
                r['scroll_idx'] = 0
                r['scroll_time'] = cur_time

        sys.stdout.write("\x1b[B")


def run():
    TERM_W = shutil.get_terminal_size((10,10)).columns

    # start curses
    #scr = curses.initscr()
    #curses.noecho()
    #curses.cbreak()

    # end curses
    #curses.echo()
    #curses.nocbreak()
    #curses.endwin()


    #print(TERM_W.columns)

    parser = argparse.ArgumentParser("mlb-term")
    parser.add_argument('-g', nargs='+', help='A list of pkids to follow')
    parser.add_argument('-l', action="store_true", help='List all active games')
    args = parser.parse_args()
    #print(args.g)
    #args =
    #print(sys.argv)
    #schedule('v1')
    #print(' ')

    if len(sys.argv) == 1 or args.l:
        schedule('v1')
        #print(' ')

    if args.g:
        query_time = -1
        render_time = -1
        query_num = 0
        render_num = 0
        datas = [None for _ in range(len(args.g))]
        tot_rows = 0
        while True:
            #
            #print(time.time())
            #print(time.time())
            #print(time.time())
            cur_time = time.time()
            if cur_time - query_time > 10:
                #os.system('cls' if os.name == 'nt' else 'clear')
                for _ in range(tot_rows):
                    #print("hhh")
                    sys.stdout.write("\x1b[A")
                tot_rows = 0
                query_num += 1
                query_time = cur_time
                for i in range(len(args.g)):
                    data = get_live_data('v1.1', args.g[i])
                    datas[i] = data
                    print_game(data)
                    print(' ')
                    tot_rows += 12

            if cur_time - render_time > 0.1:
                for _ in range(tot_rows + 1):
                    #print("hhh")
                    sys.stdout.write("\x1b[A")
                #print('top')
                print(f'q:{query_num} r:{render_num} t:{tot_rows}')
                for d in datas:
                    scroll_game(d)
                    print(' ')
                render_num += 1
                render_time = cur_time






if __name__ == '__main__':
    os.system('cls' if os.name == 'nt' else 'clear')
    run()
