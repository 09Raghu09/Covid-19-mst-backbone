"""
Helper functions collections
"""


# Built-in/Generic Imports
import os.path
import datetime
import argparse
import csv
import json
import urllib.request
import requests  # for read_url_or_cachefile
import numpy as np
import pandas as pd
#
# General Helpers
#

def read_url_or_cachefile(url: str, cachefile: str, cache_max_age: int = 15, verbose: bool = True) -> str:
    b_cache_is_recent = check_cache_file_available_and_recent(
        fname=cachefile, max_age=cache_max_age, verbose=verbose)
    if not b_cache_is_recent:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0 ',
        }
        cont = requests.get(url, headers=headers).content
        with open(cachefile, mode='wb') as fh:
            fh.write(cont)
        cont = cont.decode('utf-8')
    else:
        with open(cachefile, mode='r', encoding='utf-8') as fh:
            cont = fh.read()
    return cont


def read_json_file(filename: str):
    """
    returns list or dict
    """
    with open(filename, mode='r', encoding='utf-8') as fh:
        return json.load(fh)


def write_json(filename: str, d: dict, sort_keys: bool = False, indent: int = 1):
    with open(filename, mode='w', encoding='utf-8', newline='\n') as fh:
        json.dump(d, fh, ensure_ascii=False,
                  sort_keys=sort_keys, indent=indent)


def read_command_line_parameters() -> dict:
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sleep", help="sleep 1 second after each item",
                        default=False, action="store_true")  # store_true -> Boolean Value
    return vars(parser.parse_args())

def date_format(y: int, m: int, d: int) -> str:
    return "%04d-%02d-%02d" % (y, m, d)

#
# COVID-19 Helpers
#


def read_ref_data_de_states() -> dict:
    """
    read pop etc from ref table and returns it as dict of dict
    """
    d_states_ref = {}
    with open('data/ref_de-states.tsv', mode='r', encoding='utf-8') as f:
        csv_reader = csv.DictReader(f, delimiter="\t")
        for row in csv_reader:
            d = {}
            d['State'] = row['State']
            d['Population'] = int(row['Population'])
            d['Pop Density'] = float(row['Pop Density'])
            d_states_ref[row["Code"]] = d
    return d_states_ref


def prepare_time_series(l_time_series: list) -> list:
    """
    assumes items in l_time_series are dicts haveing the following keys: Date, Cases, Deaths
    sorts l_time_series by Date
    if cases at last entry equals 2nd last entry, than remove last entry, as sometime the source has a problem.
    loops over l_time_series and calculates the 
      Days_Past
      _New values per item/day    
      _Last_Week
    TODO: add fitted Cases_New_Slope_14 and Deaths_New_Slope_14
    """
    # some checks
    d = l_time_series[0]
    assert 'Date' in d
    assert 'Cases' in d
    assert 'Deaths' in d
    assert 'Recovered' in d
    assert isinstance(d['Date'], str)
    assert isinstance(d['Cases'], int)
    assert isinstance(d['Deaths'], int)
    assert isinstance(d['Recovered'], int)
    last_date = datetime.datetime.strptime(
        l_time_series[-1]['Date'], "%Y-%m-%d")

    # ensure sorting by date
    l_time_series = sorted(
        l_time_series, key=lambda x: x['Date'], reverse=False)

    # to ensure that each date is unique
    l_dates_processed = []

    last_cases = 0
    last_deaths = 0
    last_recovered = 0
    days_since_2_deaths = 0
    days_since_2_recovered = 0
    for i in range(len(l_time_series)):
        d = l_time_series[i]

        # ensure that each date is unique
        assert d['Date'] not in l_dates_processed
        l_dates_processed.append(d['Date'])

        this_date = datetime.datetime.strptime(d['Date'], "%Y-%m-%d")
        d['Days_Past'] = (this_date-last_date).days

        # days_since_2_deaths
        d['Days_Since_2nd_Death'] = None
        if d['Deaths'] >= 2:  # is 2 a good value?
            d['Days_Since_2nd_Death'] = days_since_2_deaths
            days_since_2_deaths += 1

        # days_since_2_recovered
        d['Days_Since_2nd_Recovered'] = None
        if d['Recovered'] >= 2:  # is 2 a good value?
            d['Days_Since_2nd_Recovered'] = days_since_2_recovered
            days_since_2_recovered += 1

        # _New since yesterday
        d['Cases_New'] = d['Cases'] - last_cases
        d['Deaths_New'] = d['Deaths'] - last_deaths
        d['Recovered_New'] = d['Recovered'] - last_recovered        
        # sometimes values are corrected, leading to negative values, which I replace by 0
        if (d['Cases_New'] < 0):
            d['Cases_New'] = 0
        if (d['Deaths_New'] < 0):
            d['Deaths_New'] = 0
        if (d['Recovered_New'] < 0):
            d['Recovered_New'] = 0
        # delta of _Last_Week = last 7 days
        d['Cases_Last_Week'] = 0
        d['Deaths_Last_Week'] = 0
        d['Recovered_Last_Week'] = 0        
        if i >= 7:
            # TM: this is correct, I double checked it ;-)
            d['Cases_Last_Week'] = d['Cases'] - l_time_series[i-7]['Cases']
            d['Deaths_Last_Week'] = d['Deaths'] - \
                l_time_series[i-7]['Deaths']
            d['Recovered_Last_Week'] = d['Recovered'] - \
                l_time_series[i-7]['Recovered']                
        # sometimes values are corrected, leading to negative values, which I replace by 0
        if (d['Cases_Last_Week'] < 0):
            d['Cases_Last_Week'] = 0
        if (d['Deaths_Last_Week'] < 0):
            d['Deaths_Last_Week'] = 0
        if (d['Recovered_Last_Week'] < 0):
            d['Recovered_Last_Week'] = 0

        # Deaths_Per_Cases
        d['Deaths_Per_Cases'] = None
        if d['Cases'] > 0 and d['Deaths'] > 0:
            d['Deaths_Per_Cases'] = round(d['Deaths'] / d['Cases'], 3)
        # Deaths_Per_Cases_Last_Week
        d['Deaths_Per_Cases_Last_Week'] = None
        if i >= 7 and d['Cases_Last_Week'] and d['Deaths_Last_Week'] and d['Cases_Last_Week'] > 0 and d['Deaths_Last_Week'] > 0:
            d['Deaths_Per_Cases_Last_Week'] = round(
                d['Deaths_Last_Week'] / d['Cases_Last_Week'], 3)

        # Recovered_Per_Cases
        d['Recovered_Per_Cases'] = None
        if d['Cases'] > 0 and d['Recovered'] > 0:
            d['Recovered_Per_Cases'] = round(d['Recovered'] / d['Cases'], 3)
        # Recovered_Per_Cases_Last_Week
        d['Recovered_Per_Cases_Last_Week'] = None
        if i >= 7 and d['Cases_Last_Week'] and d['Recovered_Last_Week'] and d['Cases_Last_Week'] > 0 and d['Recovered_Last_Week'] > 0:
            d['Recovered_Per_Cases_Last_Week'] = round(
                d['Recovered_Last_Week'] / d['Cases_Last_Week'], 3)


        last_cases = d['Cases']
        last_deaths = d['Deaths']
        last_recovered = d['Recovered']        
        l_time_series[i] = d

    return l_time_series


def add_per_million_via_lookup(d: dict, d_ref: dict, code: str) -> dict:
    pop_in_million = d_ref[code]['Population'] / 1000000
    return add_per_million(d=d, pop_in_million=pop_in_million)


def add_per_million(d: dict, pop_in_million: float) -> dict:
    for key in ('Cases', 'Deaths', 'Recovered', 'Cases_New', 'Deaths_New', 'Recovered_New', 'Cases_Last_Week', 'Deaths_Last_Week', 'Recovered_Last_Week'):
        perMillion = None
        if key in d and d[key] is not None:
            if pop_in_million:
                perMillion = round(d[key]/pop_in_million, 3)
            # else:
            #     perMillion = 0  # if pop is unknown
        d[key+'_Per_Million'] = perMillion
    return d


def check_cache_file_available_and_recent(fname: str, max_age: int = 3600, verbose: bool = False) -> bool:
    b_cache_good = True
    if not os.path.exists(fname):
        if verbose:
            print(f"No Cache available: {fname}")
        b_cache_good = False
    if (b_cache_good and time.time() - os.path.getmtime(fname) > max_age):
        if verbose:
            print(f"Cache too old: {fname}")
        b_cache_good = False
    return b_cache_good

#processing downloaded data
def calculate_sumcases_bundesland(df_rki):

  state_data = {}
  uni_states = np.unique(df_rki["Bundesland"])

  for state in uni_states:
   # print(state)
    df_state = df_rki[df_rki.Bundesland == state]
    df_state = df_state.sort_values(by=['Meldedatum'])
    df_state = df_state[["AnzahlFall","AnzahlTodesfall","AnzahlGenesen", "NeuerFall", "NeuerTodesfall", "NeuGenesen", "Meldedatum"]].groupby(by="Meldedatum").sum()

    sum_up_fall = 0
    sum_up_todfall = 0
    sum_up_genesen = 0
    sum_up_neufall = 0
    sum_up_neutodfall = 0
    sum_up_neugenesen = 0
    for i in range(len(df_state["AnzahlFall"])):
      sum_up_fall                += df_state["AnzahlFall"][i]
      df_state["AnzahlFall"][i] = sum_up_fall
      sum_up_todfall        += df_state["AnzahlTodesfall"][i]
      df_state["AnzahlTodesfall"][i] = sum_up_todfall
      sum_up_genesen        += df_state["AnzahlGenesen"][i]
      df_state["AnzahlGenesen"][i] = sum_up_genesen
      if i!=0: 
        sum_up_neufall        = df_state["AnzahlFall"][i]-df_state["AnzahlFall"][i-1]
        df_state["NeuerFall"][i] = sum_up_neufall             
        sum_up_neutodfall     = df_state["AnzahlTodesfall"][i]-df_state["AnzahlTodesfall"][i-1]
        df_state["NeuerTodesfall"][i] = sum_up_neutodfall
        sum_up_neugenesen     = df_state["AnzahlGenesen"][i]-df_state["AnzahlGenesen"][i-1]
        df_state["NeuGenesen"] [i] = sum_up_neugenesen
      else:
        sum_up_neufall        = df_state["AnzahlFall"][i]
        df_state["NeuerFall"][i] = sum_up_neufall             
        sum_up_neutodfall     = df_state["AnzahlTodesfall"][i]
        df_state["NeuerTodesfall"][i] = sum_up_neutodfall
        sum_up_neugenesen     = (df_state["AnzahlGenesen"][i])
        df_state["NeuGenesen"] [i] = sum_up_neugenesen
      state_data[state]=df_state       

  return(state_data)
def create_all_statedf(state_data):
  uni_states = list(state_data.keys())
  df = pd.DataFrame()

  for state in uni_states:
    data_dict = {}
    data_dict = { 'State_Cases': state_data[state]["AnzahlFall"], 'State_Deaths': state_data[state]["AnzahlTodesfall"], 'State_Recovered': state_data[state]["AnzahlGenesen"], 'State_newInfections': state_data[state]["NeuerFall"], 'State_newDeaths': state_data[state]["NeuerTodesfall"], 'State_newRecovered': state_data[state]["NeuGenesen"], "State" : np.repeat(state,len(state_data[state]), axis=0)}
    df_state  = pd.DataFrame(data=data_dict)
    df_state  = df_state.reset_index()
    df = df.append(pd.DataFrame(data = df_state), ignore_index=True)

  return(df)