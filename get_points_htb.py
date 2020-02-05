#!/usr/bin/python3
#
# It uses points_data.json to calculate current ownership and do an estimate to get the target score
# Usage: ./get_points_htb {type}
# 
# Where type:
# l: level
# m: test more
# u>=s: users greater or equal to system
# 
# Noob >= 0% | Script Kiddie > 5% | Hacker > 20% | Pro Hacker > 45% | Elite Hacker > 70% | Guru > 90% | Omniscient = 100%
import json
import math
import pandas as pd
import sys

ownership_level = [
    {'name': 'Noob', 'value': 0},
    {'name': 'Script Kiddie', 'value': 5},
    {'name': 'Hacker', 'value': 20},
    {'name': 'Pro Hacker', 'value': 45},
    {'name': 'Elite Hacker', 'value': 70},
    {'name': 'Guru', 'value': 90},
    {'name': 'Omniscient', 'value': 100},
]

def get_ownership(ActiveSystemOwns, ActiveUserOwns, ActiveChallengeOwns, activeMachines, activeChallenges):
    return (ActiveSystemOwns + (ActiveUserOwns / 2) + (ActiveChallengeOwns / 10)) / (activeMachines + (activeMachines / 2) + (activeChallenges / 10)) * 100

config_file = 'points_data.json'
try:
    with open(config_file) as f:
        config = json.load(f)    
except FileNotFoundError:
    print(f'Sorry, you need the config file "{config_file}"')
    sys.exit(1)

user_option = sys.argv[1] if len(sys.argv) == 2 else 'l'

ActiveSystemOwns = config['user_data']['ActiveSystemOwns']
ActiveUserOwns = config['user_data']['ActiveUserOwns']
ActiveChallengeOwns = config['user_data']['ActiveChallengeOwns']

activeMachines = config['htb_data']['activeMachines']
activeChallenges = config['htb_data']['activeChallenges']


current_ownership = get_ownership(ActiveSystemOwns, ActiveUserOwns, ActiveChallengeOwns, activeMachines, activeChallenges)

current_level = ownership_level[0]
next_level = ownership_level[1]
for o_l in ownership_level:
    if current_ownership < o_l['value']:
        next_level = o_l
        break
    else:
        current_level = o_l

print(f'Your current ownership: {current_ownership:.2f}% ({current_level["name"]})')
print(f'You need {next_level["value"]}% to get the level of {next_level["name"]}')
print('')

arr_results = {}
data = []
# users own
for j in range(0, activeMachines):
    # systems own
    for i in range(j, activeMachines):
        # challenges own
        for k in range(0, activeChallenges):
            next_user_own = ActiveUserOwns + j
            next_system_own = ActiveSystemOwns + i
            next_challenge_own = ActiveChallengeOwns + k
            tmp_ownership = get_ownership(next_system_own, next_user_own, next_challenge_own, activeMachines, activeChallenges)
            arr_results[tmp_ownership] = [j, i, k, (i + j + k)]
            data.append([j, i, k, tmp_ownership])

df = pd.DataFrame(data, columns=['users', 'systems', 'challenges', 'ownership'])
df['ownership_round'] = df['ownership'].apply(lambda x: math.floor(x))
df['sum'] = df['users'] + df['systems'] + df['challenges']

df = df.sort_values(by=['ownership_round', 'sum', 'challenges', 'users', 'systems'])

df = df[(df['users'] <= activeMachines) & (df['systems'] <= activeMachines) & (df['challenges'] <= activeChallenges)]


# if we want a desired level
if user_option == 'l' or user_option == 'u>=s':
    print('Levels:')
    next_level_int = 0
    for i, elem in enumerate(ownership_level):
        if elem['value'] <= current_ownership:
            next_level_int = i + 1
            continue
        print(f'{i}: {elem["name"]}: {elem["value"]}')

    input_question = f'Select a number (Default {next_level_int}): '
    print('-' * len(input_question))
    option = input(input_question) or next_level_int
    next_level = ownership_level[int(option)]
    print(f'Ok we are going to calculate for: {next_level["value"]}%, {next_level["name"]}')

    if user_option == 'l':
        df_next_level = df[(df['ownership'] >= next_level["value"])]
    else:
        print(f'We will filter the results for number of users greater or equal than systems')
        df_next_level = df[(df['ownership'] >= next_level["value"]) & (df['users'] >= df['systems'])]
    df_next_level = df_next_level.drop(['ownership_round', 'sum'], axis=1)

    print(df_next_level.head(25))

# if we want to manually test
elif user_option == 'm':
    plus_user = int(input('Which more users? [Default: 0] ') or 0)
    plus_root = int(input('Which more root? [Default: 0] ') or 0)
    plus_ch = int(input('Which more challenges? [Default: 0] ') or 0)

    new_ownership = get_ownership(ActiveUserOwns + plus_user, ActiveSystemOwns + plus_root, ActiveChallengeOwns + plus_ch, activeMachines, activeChallenges)
    print(f'You could get {new_ownership:.2f}%')
    sys.exit(0)
