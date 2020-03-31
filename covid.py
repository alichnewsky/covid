#!/usr/bin/env python
'''
Script to plot the SARS-nCOV-2 dataset
'''

__author__ = 'Anthony Lichnewsky'
__license__ = 'MIT License'
__version__ = '1.0'

from   datetime import datetime, timedelta
import os.path

import click
import matplotlib.pyplot as plt
import pandas as pd

# pylint: disable=fixme, bad-whitespace, bad-indentation, bad-continuation, line-too-long, invalid-name, missing-docstring

CONFIRMED_DATASET = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'

DEATHS_DATASET = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'

@click.group()
def cli():
        '''
        Command to download and plot Johns Hopkins SARS-nCOV-2 dataset
        '''
        pass

def _download():
        # use urllib2 instead ?
        pd.read_csv( CONFIRMED_DATASET ).to_csv( 'time_series_covid19_confirmed_global.csv' )
        pd.read_csv( DEATHS_DATASET    ).to_csv( 'time_series_covid19_deaths_global.csv'    )

@cli.command()
def download():
        '''
        download Johns Hopkins SARS-nCOV-2 dataset
        '''
        click.echo( 'downloading Johns Hopkins dataset from github.com' )

        _download()

def get_countries_of_interest():
        countries_of_interest = ["France", "Italy", "United Kingdom", "US", "China" ]
        return countries_of_interest

def get_states_of_interest():
        states_of_interest = ["California", "Washington", "New York", "Texas" ]
        return states_of_interest

def get_european_countries():
        european_countries = [
                'Albania',
                'Austria',
                'Belarus',
                'Belgium',
                'Bosnia',
                'Bulgaria',
                'Croatia',
                'Cyprus',
                'Czech Republic',
                'Denmark',
                'Estonia',
                'Finland',
                'France',
                'Germany',
                'Greece',
                'Hungary',
                'Latvia',
                'Ireland',
                'Italy',
                'Lithuania'
                'Luxembourg',
                'Malta',
                'Netherlands',
                'Norway',
                'Portugal',
                'Poland',
                'Romania',
                'San Marino',
                'Serbia',
                'Slovakia',
                'Slovenia',
                'Spain',
                'Sweden',
                'Switzerland',
                'United Kingdom'
        ]
        return european_countries

def get_eu_countries():
        eu_countries = [
                'Austria',
                'Belgium',
                'Bulgaria',
                'Croatia',
                'Cyprus',
                'Czech Republic',
                'Denmark',
                'Estonia',
                'Finland',
                'France',
                'Germany',
                'Greece',
                'Hungary',
                'Ireland',
                'Italy',
                'Latvia',
                'Lithuania',
                'Luxembourg',
                'Malta',
                'Netherlands',
                'Poland',
                'Portugal',
                'Romania',
                'Slovakia',
                'Slovenia',
                'Spain',
                'Sweden'
        ]
        return eu_countries

@cli.command()
@click.option( '--draw/--no-draw', default=True, help='plot on screen' )
@click.option( '--save', is_flag=True, default=False, help='save as PNG' )
def plot( draw, save ):
        '''
        Plot dataset
        '''

        if draw is False and save is False :
                click.echo( 'nothing to plot' )
                return

        cfile = 'time_series_covid19_confirmed_global.csv'
        dfile = 'time_series_covid19_deaths_global.csv'

        now = datetime.now()

        if  ( os.path.isfile( cfile ) is False ) or \
            ( os.path.isfile( dfile ) is False ) or \
            ( now - datetime.fromtimestamp( os.path.getmtime( cfile ) ) ) > timedelta( hours=2 ) or \
            ( now - datetime.fromtimestamp( os.path.getmtime( dfile ) ) ) > timedelta( hours=2 )     :
                click.echo( 'downloading files' )
                _download()

        click.echo( 'reading dataset from disk' )

        df_confd = pd.read_csv( 'time_series_covid19_confirmed_global.csv' )
        df_death = pd.read_csv( 'time_series_covid19_deaths_global.csv'    )

        for df in [ df_confd, df_death]:
                df.dropna(axis=1, how='all', inplace=True )
                # fillna ?

        figsize=(60,30)
        fontsize=20

        days_to_ignore = 30
        window_size = 7

        _, (ax1, ax2, ax3) = plt.subplots(1,3, figsize=figsize)

        countries_of_interest = get_countries_of_interest()

        for country in countries_of_interest:

                data_country = df_confd.loc[df_confd['Country/Region'] == country].filter(regex='.*/20',axis=1).sum(0)
                diff_country = data_country.diff().dropna()
                rolling_windowed_sum_diff_country = diff_country.rolling( window_size, win_type='boxcar' ).sum().dropna() / window_size

                for ax in [ax1]:#, ax2:
                        ax.plot(data_country[(5+days_to_ignore):], lw=3, alpha=0.5, label=country)
                for ax in [ax3]:#, ax2:
                        ax.plot(data_country[(5+window_size-1+days_to_ignore+1):],
                                rolling_windowed_sum_diff_country[(5+days_to_ignore):],
                                lw=3, alpha=0.5, label=country)

        european_countries = get_european_countries()

        data_europe = df_confd.loc[df_confd['Country/Region'].isin(european_countries) ].filter(regex='.*/20',axis=1).sum(0)
        diff_europe = data_europe.diff().dropna()
        rolling_windowed_sum_diff_europe = diff_europe.rolling( window_size, win_type='boxcar').sum().dropna() / window_size

        #death_europe  = df_death.loc[df_death['Country/Region'].isin(european_countries) ].filter(regex='.*/20',axis=1).sum(0)

        for ax in [ax1]:
                ax.plot(data_europe[(5+days_to_ignore):], lw=3, alpha=0.5, label='Europe')

        for ax in [ax3]:
                ax.plot( data_europe[(5+window_size-1+days_to_ignore+1):],
                         rolling_windowed_sum_diff_europe[(5+days_to_ignore):],
                         lw=3,
                         alpha=0.5,
                         label='EU'
                )

        data_china = df_confd.loc[df_confd['Country/Region'].isin(['China']) ].filter(regex='.*/20',axis=1).sum(0)
        diff_china = data_china.diff().dropna()
        rolling_windowed_sum_diff_china = diff_china.rolling( window_size, win_type='boxcar').sum().dropna() / window_size
        ax3.plot( data_china[(5+window_size-1+1):],
                  rolling_windowed_sum_diff_china[(5):],
                  lw=3,
                  alpha=0.5,
                  label='China'
        )

        for country in countries_of_interest:
                data_country = df_confd.loc[df_confd['Country/Region'] == country].filter(regex='.*/20',axis=1).sum(0)
                diff_country = data_country.diff().dropna()
                smoothed_diff_country = diff_country.rolling( window_size, win_type='boxcar' ).sum().dropna() / window_size
                for ax in [ax2]:
                        ax.plot( smoothed_diff_country[(5+days_to_ignore+window_size-1):],
                                 lw=3,
                                 alpha=0.5,
                                 label=country
                        )

        ax1.set_title("Confirmed cases of coronavirus in some countries ")
        ax2.set_title("new cases from corona virus in same countries")
        ax3.set_title("smoothed new cases per day vs total cases from corona virus in same countries.\n"
                      "straight line = exponential growth of total cases"
        )

        for ax in [ax1, ax2, ax3]:
                ax.xaxis.set_major_locator(plt.MaxNLocator(12))
                ax.legend()

                for item in ([ ax.title, ax.xaxis.label, ax.yaxis.label ]
                             + ax.get_xticklabels()
                             + ax.get_yticklabels()
                             + ax.get_legend().get_texts()  ):
                        item.set_fontsize(fontsize)

                plt.setp( ax.get_xticklabels(), rotation=90)

        ax3.set_xscale('log')
        ax3.set_yscale('log')

        if save :
                click.echo( 'saving to PNG...' )
                plt.savefig("coronavirus.png")

        if draw :
                click.echo( 'plotting...' )
                plt.show()

if __name__ == '__main__':
        cli()
