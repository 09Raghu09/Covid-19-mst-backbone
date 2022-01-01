#!/usr/bin/python3
# -*- coding: utf-8 -*-


# Built-in/Generic Imports

import time
import urllib.request
import csv
import pandas as pd
import numpy as np
# import json

# from matplotlib import pyplot as plt

# my helper modules
import helper

args = helper.read_command_line_parameters()
download_file = 'cache/RKI_COVID19.csv'
processed_file = 'cache/RKI_COVID19_preprocessed.csv'


def download_new_data():
    url = "https://opendata.arcgis.com/datasets/dd4580c810204019a7b8eb3e0b329dd6_0.csv"
    filedata = urllib.request.urlopen(url)
    datatowrite = filedata.read()
    with open(download_file, mode='wb') as f:
        f.write(datatowrite)
def processing():
    df_rki = pd.read_csv(download_file, parse_dates=['Meldedatum'], squeeze=True)
    state_data=helper.calculate_sumcases_bundesland(df_rki)
    df_state_data = helper.create_all_statedf(state_data)
    uni_dates = np.unique(df_state_data["Meldedatum"])
    df = df_state_data.groupby('Meldedatum')['State'].nunique()
    lista=df[df==16].index.values
    df_state_data=df_state_data[df_state_data['Meldedatum'].isin(lista)]
    df_state_data.to_csv('cache/RKI_COVID19_preprocessed.csv', encoding='utf-8-sig')
   
def read_csv_to_dict() -> dict:
    """
    read and convert the source csv file, containing: federalstate,infections,deaths,date,newinfections,newdeaths
    re-calc _New
    add _Per_Million
    add Fitted Doubling time
    """

    global d_states_ref
    # Preparations
    d_states_data = {'BW': [], 'BY': [], 'BE': [], 'BB': [], 'HB': [], 'HH': [], 'HE': [], 'MV': [
    ], 'NI': [], 'NW': [], 'RP': [], 'SL': [], 'SN': [], 'ST': [], 'SH': [], 'TH': []}
    # add German sum
    #d_states_data['DE-total'] = []
    #d_german_sums = {}  # date -> 'infections', 'deaths', 'new infections', 'new deaths'

    # data body
    with open(processed_file, mode='r', encoding='utf-8') as f:
        csv_reader = csv.DictReader(f, delimiter=",")
        for row in csv_reader:
            d = {}
            s = row['Meldedatum']
            l = s.split("-")
            d['Date'] = helper.date_format(
                int(l[0]), int(l[1]), int(l[2]))
            #print(int(row["infections"]))
            d['Cases'] = int(row["State_Cases"])
            d['Deaths'] = int(row["State_Deaths"])
            d['Recovered'] = int(row["State_Recovered"])          
            if row["State"] == 'Baden-Württemberg':
                d_states_data['BW'].append(d)
            elif row["State"] == 'Bayern':
                d_states_data['BY'].append(d)
            elif row["State"] == 'Berlin':
                d_states_data['BE'].append(d)
            elif row["State"] == 'Brandenburg':
                d_states_data['BB'].append(d)
            elif row["State"] == 'Bremen':
                d_states_data['HB'].append(d)
            elif row["State"] == 'Hamburg':
                d_states_data['HH'].append(d)
            elif row["State"] == 'Hessen':
                d_states_data['HE'].append(d)
            elif row["State"] == 'Niedersachsen':
                d_states_data['NI'].append(d)
            elif row["State"] == 'Nordrhein-Westfalen':
                d_states_data['NW'].append(d)
            elif row["State"] == 'Mecklenburg-Vorpommern':
                d_states_data['MV'].append(d)
            elif row["State"] == 'Rheinland-Pfalz':
                d_states_data['RP'].append(d)
            elif row["State"] == 'Saarland':
                d_states_data['SL'].append(d)
            elif row["State"] == 'Sachsen':
                d_states_data['SN'].append(d)
            elif row["State"] == 'Sachsen-Anhalt':
                d_states_data['ST'].append(d)
            elif row["State"] == 'Schleswig-Holstein':
                d_states_data['SH'].append(d)
            elif row["State"] == 'Thüringen':
                d_states_data['TH'].append(d)
            else:
                print("ERROR: unknown state")
                quit()


    for code in d_states_data.keys():
        l_time_series = d_states_data[code]
        
        l_time_series = helper.prepare_time_series(l_time_series)
        #print(l_time_series)
        # add days past and per million
        for i in range(len(l_time_series)):
            d = l_time_series[i]
            # add per Million rows
            d = helper.add_per_million_via_lookup(d, d_states_ref, code)

        d_states_data[code] = l_time_series

        if args["sleep"]:
            time.sleep(1)

    return d_states_data


def export_data(d_states_data: dict):
    # export JSON and CSV
    for code in d_states_data.keys():
        #print(code)
        outfile = f'data/de-states/de-state-{code}.tsv'
        l_time_series = d_states_data[code]

        helper.write_json(
            f'data/de-states/de-state-{code}.json', l_time_series)

        with open(outfile, mode='w', encoding='utf-8', newline='\n') as fh:
            csvwriter = csv.DictWriter(fh, delimiter='\t', extrasaction='ignore', fieldnames=[
                'Days_Past', 'Date',
                'Cases', 'Deaths', 'Recovered',
                'Cases_New', 'Deaths_New', 'Recovered_New',
                'Cases_Last_Week', 'Deaths_Last_Week', 'Recovered_Last_Week',
                'Cases_Per_Million', 'Deaths_Per_Million', 'Recovered_Per_Million',
                'Cases_New_Per_Million', 'Deaths_New_Per_Million', 'Recovered_New_Per_Million',
                'Cases_Last_Week_Per_Million', 'Deaths_Last_Week_Per_Million', 'Recovered_Last_Week_Per_Million',
                'Cases_Doubling_Time', 'Deaths_Doubling_Time', 'Recovered_Doubling_Time'
            ]
            )
            csvwriter.writeheader()
            for d in l_time_series:
                csvwriter.writerow(d)


def export_latest_data(d_states_data: dict):
    d_states_latest = dict(d_states_ref)
    for code in d_states_latest.keys():
        assert code in d_states_data.keys()
        l_state = d_states_data[code]
        d_latest = l_state[-1]
        d_states_latest[code]['Date_Latest'] = d_latest['Date']
        for key in ('Cases', 'Deaths', 'Recovered', 'Cases_New', 'Deaths_New', 'Recovered_New', 'Cases_Per_Million', 'Deaths_Per_Million', 'Recovered_Per_Million'):
            d_states_latest[code][key] = d_latest[key]
    with open('data/de-states/de-states-latest.tsv', mode='w', encoding='utf-8', newline='\n') as fh:
        csvwriter = csv.DictWriter(fh, delimiter='\t', extrasaction='ignore',
                                   fieldnames=('State', 'Code', 'Population', 'Pop Density',
                                               'Date_Latest',
                                               'Cases', 'Deaths', 'Recovered',
                                               'Cases_New', 'Deaths_New', 'Recovered_New',
                                               'Cases_Per_Million',
                                               'Deaths_Per_Million', 'Recovered_Per_Million'
                                              )
                                   )
        csvwriter.writeheader()
        for code in sorted(d_states_latest.keys()):
            d = d_states_latest[code]
            d['Code'] = code

            csvwriter.writerow(
                d
            )
        del d, code

d_states_ref = helper.read_ref_data_de_states()


download_new_data()
processing()
d_states_data = read_csv_to_dict()

export_data(d_states_data)
export_latest_data(d_states_data)

# 1
