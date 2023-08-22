import pandas as pd
from cassia.old.tools import prompt_hotkeys
from cassia.old import reports
import matplotlib.pyplot as plt


def group_data(data, field='category', threshold=0.10):
    grouped_data = data[['duration', field]].groupby([field]).sum(numeric_only=False)
    sorted_grouped_data = grouped_data.sort_values('duration', ascending=False).reset_index()
    total_minutes = sum(sorted_grouped_data['duration'])
    num_categories = sum([x > (total_minutes*threshold) for x in sorted_grouped_data['duration']])
    top_buckets = sorted_grouped_data[0:num_categories]
    misc_bucket = pd.DataFrame(data={
        field: ['Other'],
        'duration': [sorted_grouped_data['duration'][num_categories:].sum()]
    })
    return pd.concat([top_buckets, misc_bucket])


def pie(grouped_df, title, filename, field):
    plt.style.use('ggplot')
    grouped_df.plot(labels=grouped_df[field], kind='pie', y='duration', autopct='%1.1f%%',
                    title=title, startangle=90, radius=1, figsize=(8, 8), fontsize=12, legend=None, labeldistance=1.1)
    plt.savefig(f'{filename}.pdf')

def list_unique_values(df, field):
    return sorted(list(set(df[field].values)))


def filter_df(df, field, value, date=None):
    if date == "Before":
        return df[df[field] < value]
    if date == "After":
        return df[df[field] > value]
    if date is None:
        return df[df[field] == value]

def analysis_menu(df):
    report_list = []
    for report in dir(reports):
        if (report not in ['cassia', 'tools', 'analysis', 'dt', 'today', 'one_week_prior']) and not (report[0] == '_'):
            report_list.append(report)
    report_name = prompt_hotkeys('name', report_list, allow_new=False)
    vars(reports)[report_name](df)

import datetime as dt
import numpy as np
#import xarray as xr


def check_datetime_validity(string, date_format):
    """ utility for checking if a string matches the format '%Y-%m' etc. """
    try:
        dt.datetime.strptime(string, date_format)
        return True
    except ValueError:
        return False


def df_to_xarray(df):
    """ Take a pandas datalog and make a 2-D array showing the total time spent on each category on each day"""
    durs = df.groupby(['category', pd.Grouper(key='time', freq='D')])['duration'].sum()
    ds = durs.to_xarray().fillna(0)  # convert to xarray
    # # normalize to 1440 minutes per day
    # ds = ds * 1440 / ds.groupby('time').map(sum)
    # Sort by total time spent in each category
    cat_times = ds.groupby('category').map(sum)
    ds = ds.sortby(cat_times, ascending=False)
    return ds


# utility to convert a number of minutes back to a display time
def display_minutes(n, min_n=0):
    return f'{int(n) // 60}:{int(n) % 60:0>2}' if n > min_n else ''


# utility to convert a date to the day of the week
def display_date(date: np.datetime64):
    datetime = dt.datetime.utcfromtimestamp(int(date) / 1e9)
    return ('Monday', 'Tuesday', 'Wednesday', 'Thursday',
            'Friday', 'Saturday', 'Sunday')[datetime.weekday()]


def draw_figure(ds):
    plt.style.use('ggplot')
    fig = plt.figure(figsize=(10, 7))
    gs = fig.add_gridspec(1, 1)
    ax = fig.add_subplot(gs[0])
    # create a stacked bar chart each category is its own bar chart
    # the top of each bar is the bottom of the next one
    bottom = 0
    weekdays = [display_date(d) for d in ds.time]
    for cat in ds.category.data:
        heights = ds.sel(category=cat).data
        label = f'{display_minutes(sum(heights)):>5} {cat}'
        bar = ax.bar(x=weekdays, height=ds.sel(category=cat),
                     bottom=bottom, width=0.5, label=label)
        bar_labels = [display_minutes(n, min_n=45) for n in heights]
        ax.bar_label(bar, labels=bar_labels, label_type='center', fontsize=8)
        bottom += heights

    ax.get_yaxis().set_visible(0)
    ax.set_ylim(bottom=0, top=1440)
    ax.legend(bbox_to_anchor=(1, 1))  # put the legend outside on the right
    fig.tight_layout()
    return fig


def logfile_to_figure(df):
    ds = df_to_xarray(df)
    print(ds)
    draw_figure(ds).savefig('last_week_bar_chart.pdf')
