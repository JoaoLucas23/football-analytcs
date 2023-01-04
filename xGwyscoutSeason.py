# -*- coding: utf-8 -*-
"""
Created on Tue Jan  3 20:22:19 2023

@author: jllgo
"""

import os
from mplsoccer import Sbopen
import pandas as pd
import numpy as np
import warnings
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import matplotlib as mpl 
import json

competition = input("Desired League: ")

event_path = "H:\Documentos\SaLab\Soccermatics\Wyscout Data\events_"+competition+".json"
matches_path = "H:\Documentos\SaLab\Soccermatics\Wyscout Data\matches_"+competition+".json"
teams_path = os.path.join('H:\Documentos\SaLab\Soccermatics','Wyscout Data', 'teams.json')

with open(teams_path) as f:
    data = json.load(f)
    
teams_df = pd.DataFrame()    
teams_df = pd.concat([teams_df, pd.DataFrame(data)])

teams_df.rename(columns = {'wyId':'teamId'}, inplace=True)
teams_df.rename(columns = {'name':'teamName'}, inplace=True)
to_merge = teams_df[['teamId', 'teamName']]

with open(matches_path) as f:
    data = json.load(f)
    
matches_df = pd.DataFrame()    
matches_df = pd.concat([matches_df, pd.DataFrame(data)])

with open(event_path) as f:
    data = json.load(f)
    
events_df = pd.DataFrame()    
events_df = pd.concat([events_df, pd.DataFrame(data)])   
shots_df = events_df.loc[events_df.eventName == 'Shot']

season = "2017/2018"

teamStats_df = pd.DataFrame(columns=["team","games","points","gf","ga","gd","xG","xGA","xGD"])
competition_teams = matches_df.winner.unique()
for team in competition_teams:
    if team > 0:
        name = teams_df.loc[teams_df.teamId == team]['teamName'].values[0]
        row = {"team":name,"games":0,"points":0,"gf":0,"ga":0,"gd":0,"xG":0,"xGA":0,"xGD":0}
        teamStats_df = teamStats_df.append(row, ignore_index=True)
    
soma = 0
for i,  match in matches_df.iterrows():
    teams_ids = []
    for key in match["teamsData"]:      
        teams_ids.append(int(key)) 
    home_team = teams_df.loc[teams_df.teamId == teams_ids[0]]['teamName'].values[0]
    away_team = teams_df.loc[teams_df.teamId == teams_ids[1]]['teamName'].values[0]
    home_id = teams_ids[0]
    away_id = teams_ids[1]
    home_idx = teamStats_df.loc[teamStats_df.team==home_team].index.values[0]
    away_idx = teamStats_df.loc[teamStats_df.team==away_team].index.values[0]
    
    home_pts = teamStats_df.at[home_idx,'points']
    away_pts = teamStats_df.at[away_idx,'points']
    
    if match.winner == home_id:
        teamStats_df.at[home_idx,'points'] = 3 + home_pts
    elif match.winner == away_id:
        teamStats_df.at[away_idx,'points'] = 3 + away_pts
    elif match.winner == 0:
        teamStats_df.at[home_idx,'points'] = 1 + home_pts
        teamStats_df.at[away_idx,'points'] = 1 + away_pts

    home_gls = match['teamsData'][str(home_id)]['score']
    away_gls = match['teamsData'][str(away_id)]['score']
    
    home_gf = teamStats_df.at[home_idx,'gf']
    away_ga = teamStats_df.at[away_idx,'ga']
    home_ga = teamStats_df.at[home_idx,'ga']
    away_gf = teamStats_df.at[away_idx,'gf']

    teamStats_df.at[home_idx,'gf'] = home_gf + home_gls
    teamStats_df.at[away_idx,'ga'] = away_ga + home_gls
    teamStats_df.at[home_idx,'ga'] = home_ga + away_gls
    teamStats_df.at[away_idx,'gf'] = away_gf + away_gls
    
    shots = shots_df.loc[shots_df.matchId == match.wyId]
