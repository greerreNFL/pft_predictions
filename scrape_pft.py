from googlesearch import search
from datetime import datetime
import time
import random
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy

## search pft for any url with the pfts-week stub and picks ##
q = 'site:profootballtalk.nbcsports.com inurl:pfts-week- inurl:picks'

pft_links = []

for i in search(
    q,
    tld = 'com',
    lang = 'en',
    num = 100,
    start = 0,
    stop = 250,
    pause = 3
):
    pft_links.append(i)



ow = []
## function that will scrape and parse one weeks worth of picks based on a url ##
def get_picks(url):
    ## pull link and parse html ##
    raw = requests.get(url)
    parsed = BeautifulSoup(raw.content, 'html.parser')
    ## picks are all in <p> so get all p's and look for 'Florios Pick:'
    pick_texts = []
    for p in parsed.find_all('p'):
        if 'Florio’s pick:' in p.text:
            pick_texts.append(p.text)
        else:
            pass
    if len(pick_texts) > 0:
        print('     Found {0} picks. Trying to parse...'.format(len(pick_texts)))
        for pick_text in pick_texts:
            try:
                season_week = extract_week(parsed)
                picks = extract_pick(pick_text)
                ow.append({
                    'season' : season_week[0],
                    'week' : season_week[1],
                    'team_one' : picks[0],
                    'score_one' : picks[1],
                    'team_two' : picks[2],
                    'score_two' : picks[3],
                })
            except:
                print('          Parse failed...')
    else:
        print('     Didnt find picks')


## helper function to extract week number ##
def extract_week(parsed_html):
    text_week_dict = {
        'one' : 1,
        'two' : 2,
        'three' : 3,
        'four' : 4,
        'five' : 5,
        'six' : 6,
        'seven' : 7,
        'eight' : 8,
        'nine' : 9,
        'ten' : 10,
        'eleven' : 11,
        'twelve' : 12,
        'thirteen' : 13,
        'fourteen' : 14,
        'fifteen' : 15,
        'sixteen' : 16,
        'seventeen' : 17,
    }
    ## turn posted on string into a datetime ##
    post_date = parsed_html.find_all('span', {'class' : 'posted-on'})[0].text
    post_date = post_date.split(',')[0] + post_date.split(',')[1]
    post_date = datetime.strptime(post_date,'%B %d %Y')
    ## convert date into season ##
    if post_date.month < 8:
        season = post_date.year - 1
    else:
        season = post_date.year
    ## parse week from header ##
    post_name = parsed_html.find_all('h1', {'class' : 'entry-title'})[0].text
    try:
        week = int(post_name.split('Week ')[1].split(' ')[0])
    except:
        week = int(text_week_dict[post_name.split('Week ')[1].split(' ')[0].lower()])
    return [season, week]


## helper function to parse pick text ##
def extract_pick(pick_text):
    teams = pick_text.split(': ')[1]
    team_score_one = teams.split(', ')[0]
    team_one = team_score_one.split(' ')[0]
    score_one = int(team_score_one.split(' ')[1])
    team_score_two = teams.split(', ')[1]
    team_two = team_score_two.split(' ')[0]
    score_two = int(team_score_two.split(' ')[1].split('.')[0])
    return [team_one, score_one, team_two, score_two]


pft_df = None
## iterate through links ##
for i in pft_links:
    time.sleep(2 + random.random() * 2)
    try:
        get_picks(i)
    except:
        print('parser_failed')
    pft_df = pd.DataFrame(ow)



## pull in game data ##
game_df = pd.read_csv('https://raw.githubusercontent.com/leesharpe/nfldata/master/data/games.csv')

## standardize franchise names ##
pbp_team_standard_dict = {

    'ARI' : 'ARI',
    'ATL' : 'ATL',
    'BAL' : 'BAL',
    'BUF' : 'BUF',
    'CAR' : 'CAR',
    'CHI' : 'CHI',
    'CIN' : 'CIN',
    'CLE' : 'CLE',
    'DAL' : 'DAL',
    'DEN' : 'DEN',
    'DET' : 'DET',
    'GB'  : 'GB',
    'HOU' : 'HOU',
    'IND' : 'IND',
    'JAC' : 'JAX',
    'JAX' : 'JAX',
    'KC'  : 'KC',
    'LA'  : 'LAR',
    'LAC' : 'LAC',
    'LV'  : 'OAK',
    'MIA' : 'MIA',
    'MIN' : 'MIN',
    'NE'  : 'NE',
    'NO'  : 'NO',
    'NYG' : 'NYG',
    'NYJ' : 'NYJ',
    'OAK' : 'OAK',
    'PHI' : 'PHI',
    'PIT' : 'PIT',
    'SD'  : 'LAC',
    'SEA' : 'SEA',
    'SF'  : 'SF',
    'STL' : 'LAR',
    'TB'  : 'TB',
    'TEN' : 'TEN',
    'WAS' : 'WAS',

}

game_df['home_team'] = game_df['home_team'].replace(pbp_team_standard_dict)
game_df['away_team'] = game_df['away_team'].replace(pbp_team_standard_dict)

## replace game_id using standardized franchise names ##
game_df['game_id'] = (
    game_df['season'].astype('str') +
    '_' +
    game_df['week'].astype('str').str.zfill(2) +
    '_' +
    game_df['away_team'] +
    '_' +
    game_df['home_team']
)


## convert pft team names and join ##
pft_team_standard_dict = {
    '49ers' : 'SF',
    'Bears' : 'CHI',
    'Bengals' : 'CIN',
    'Bills' : 'BUF',
    'Broncos' : 'DEN',
    'Browns' : 'CLE',
    'Buccaneers' : 'TB',
    'Cardinals' : 'ARI',
    'Chargers' : 'LAC',
    'Chiefs' : 'KC',
    'Colts' : 'IND',
    'Cowboys' : 'DAL',
    'Dolphins' : 'MIA',
    'Eagles' : 'PHI',
    'Falcon' : 'ATL',
    'Falcons' : 'ATL',
    'Giants' : 'NYG',
    'Jaguars' : 'JAX',
    'Jets' : 'NYJ',
    'Lions' : 'DET',
    'Packers' : 'GB',
    'Panthers' : 'CAR',
    'Patriots' : 'NE',
    'Raiders' : 'OAK',
    'Rams' : 'LAR',
    'Ravens' : 'BAL',
    'Saints' : 'NO',
    'Seahawk' : 'SEA',
    'Seahawks' : 'SEA',
    'Steelers' : 'PIT',
    'Texans' : 'HOU',
    'Titans' : 'TEN',
    'Vikings' : 'MIN',
    'Washington' : 'WAS',
    'Washinton' : 'WAS',
    ' Broncos' : 'DEN',
    ' Chargers' : 'LAC',
    ' Panthers' : 'CAR',
    ' Ravens' : 'BAL',
}
pft_df['team_one'] = pft_df['team_one'].replace(pft_team_standard_dict)
pft_df['team_two'] = pft_df['team_two'].replace(pft_team_standard_dict)

pft_df = pft_df.drop_duplicates()

## home away not specified, so try to joine two vers ##
pft_one_df = pft_df.copy().rename(columns={
    'team_one' : 'home_team',
    'team_two' : 'away_team',
    'score_one' : 'home_score_pft_one',
    'score_two' : 'away_score_pft_one',
})

## home away not specified, so try to joine two vers ##
pft_two_df = pft_df.copy().rename(columns={
    'team_one' : 'away_team',
    'team_two' : 'home_team',
    'score_one' : 'away_score_pft_two',
    'score_two' : 'home_score_pft_two',
})


## joine to game file ##
game_df = game_df[[
    'game_id', 'season', 'week', 'home_team', 'away_team',
    'home_score', 'away_score', 'spread_line'
]]
game_df['home_margin'] = game_df['home_score'] - game_df['away_score']
game_df['home_spread_margin'] = game_df['home_margin'] - game_df['spread_line']

## no games that havent been played ##
game_df = game_df[~pd.isnull(game_df['home_score'])]

## merge first ##
game_df = pd.merge(
    game_df,
    pft_one_df,
    on=['season', 'week', 'home_team', 'away_team'],
    how='left'
)

game_df = pd.merge(
    game_df,
    pft_two_df,
    on=['season', 'week', 'home_team', 'away_team'],
    how='left'
)

## combine ##
game_df['home_score_pft'] = game_df['home_score_pft_one'].combine_first(game_df['home_score_pft_two'])
game_df['away_score_pft'] = game_df['away_score_pft_one'].combine_first(game_df['away_score_pft_two'])

## remove old columns ##
game_df = game_df.drop(columns=[
    'home_score_pft_one', 'home_score_pft_two',
    'away_score_pft_one', 'away_score_pft_two'
])

## only keep matching games ##
game_df = game_df[
    ~pd.isnull(game_df['home_score_pft']) &
    ~pd.isnull(game_df['away_score_pft'])
]


## scoring logic ##
game_df['pft_home_spread_prediction'] = game_df['home_score_pft'] - game_df['away_score_pft']
## drop games where spreads are equal ##
game_df = game_df[game_df['spread_line'] != game_df['pft_home_spread_prediction']]

game_df['pft_bet_home'] = numpy.where(
    game_df['pft_home_spread_prediction'] > game_df['spread_line'],
    1,
    0
)

## bet result ##
game_df['pft_bet_result'] = numpy.where(
    ## push ##
    game_df['home_spread_margin'] == 0,
    numpy.nan,
    ## result ##
    numpy.where(
        ## bet home win ##
        (
            (game_df['pft_bet_home'] == 1) &
            (game_df['home_spread_margin'] > 0)
        ) |
        ## or bet away win ##
        (
            (game_df['pft_bet_home'] == 0) &
            (game_df['home_spread_margin'] < 0)
        ),
        1,
        0
    )
)
game_df['W'] = numpy.where(game_df['pft_bet_result'] == 1, 1, 0)
game_df['L'] = numpy.where(game_df['pft_bet_result'] == 0, 1, 0)
game_df['P'] = numpy.where(pd.isnull(game_df['pft_bet_result']), 1, 0)
game_df['return'] = numpy.where(
    game_df['pft_bet_result'] == 1,
    100,
    numpy.where(
        game_df['pft_bet_result'] == 0,
        -110,
        0
    )
)

## aggregate results ##
## dummy to agg on ##
game_df['service'] = 'pft'
agg_df = game_df.groupby(['service']).agg(
    total_predictions = ('pft_bet_home', 'count'),
    W = ('W', 'sum'),
    L = ('L', 'sum'),
    P = ('P', 'sum'),
    ATS = ('pft_bet_result', 'mean'),
    Avg_Return = ('return', 'mean'),
    Total_Return = ('return', 'sum'),
).reset_index()

print(agg_df)
