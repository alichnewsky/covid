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
from countryinfo import CountryInfo


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
#        countries_of_interest = ["France", "Italy", "United Kingdom", "US", "China" ]
        countries_of_interest = ["France", "Italy", "United Kingdom", "Israel" ]
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
@click.option( '--relative', is_flag=True, default=False, help='plot per stats per million inhabitants' )
@click.option( '--days_to_ignore', default=300, help='days to ignore since the beginning of pandemic' )
def plot( draw, save, relative, days_to_ignore ):
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

        # fixme : make a parameter of both of these
        #days_to_ignore = 200

        # this could be a parameter, but very tricky....
        window_size = 7

        _, ((ax1, ax2), (ax3, ax4))  = plt.subplots(2,2, figsize=figsize)

        countries_of_interest = get_countries_of_interest()

        populations = { c : CountryInfo(c).info()['population'] for c in countries_of_interest }
        print( populations)

        def plot_dataset( df, countries_of_interest, ax1, ax2  ):
                
                for country in countries_of_interest:

                        data_country = df.loc[df['Country/Region'] == country].filter(regex='.*/2[01]',axis=1).sum(0)
                        if relative:
                                mhab = populations[country] * 1e-6
                                data_country /= mhab
                        #diff_country = data_country.diff().dropna()
                        #rolling_windowed_sum_diff_country = diff_country.rolling( window_size, win_type='boxcar' ).sum().dropna() / window_size

                        ax1.plot(data_country[(5+days_to_ignore):], lw=3, alpha=0.5, label=country)

                for country in countries_of_interest:
                        data_country = df.loc[df['Country/Region'] == country].filter(regex='.*/2[01]',axis=1).sum(0)
                        if relative:
                                mhab = populations[country] * 1e-6
                                data_country /= mhab

                        diff_country = data_country.diff().dropna()
                        smoothed_diff_country = diff_country.rolling( window_size, win_type='boxcar' ).sum().dropna() / window_size

                        ax2.plot( smoothed_diff_country[(5+days_to_ignore+window_size-1):],
                                  lw=3,
                                  alpha=0.5,
                                  label=country
                        )

        plot_dataset( df_confd, countries_of_interest, ax1, ax2 )
        plot_dataset( df_death, countries_of_interest, ax3, ax4 )

        if relative:
                ax1.set_title("cumulative cases per million inhabitants" )
                ax2.set_title("daily new cases per million inhabitants" )
                ax3.set_title("cumulative deaths per million inhabitants" )
                ax4.set_title("new deaths per million inhabitants")
        else:
                ax1.set_title("cumulative cases")
                ax2.set_title("new cases")
                ax3.set_title("cumulative deaths")
                ax4.set_title("new deaths")

        for ax in [ax1, ax2, ax3, ax4]:
                ax.xaxis.set_major_locator(plt.MaxNLocator(12))
                ax.legend()

                for item in ([ ax.title, ax.xaxis.label, ax.yaxis.label ]
                             + ax.get_xticklabels()
                             + ax.get_yticklabels()
                             + ax.get_legend().get_texts()  ):
                        item.set_fontsize(fontsize)

                plt.setp( ax.get_xticklabels(), rotation=90)


        if save :
                click.echo( 'saving to PNG...' )
                plt.savefig("coronavirus.png")

        if draw :
                click.echo( 'plotting...' )
                plt.show()

if __name__ == '__main__':
        cli()
