import cassia.old.analysis as analysis
import time
import cassia.old.tools as tools
import datetime as dt

# Constants
today = dt.datetime.now().replace(hour=0,minute=0,second=0)
one_week_prior = today - dt.timedelta(days=7)

def last_week_pie(df):
    t = time.time()
    df = tools.add_durations(df)
    df = analysis.filter_df(df, 'time', one_week_prior, date='After')
    df = analysis.filter_df(df, 'time', today, date='Before')
    grouped_df = analysis.group_data(df, threshold=0.03)
    print(grouped_df)
    analysis.pie(grouped_df, f'Category breakdown from {one_week_prior.strftime("%Y-%m-%d")} to {(today - dt.timedelta(days=1)).strftime("%Y-%m-%d")}', 'last_week_pie', 'category')
    print(time.time() - t)

def last_week_bar(df):
    t = time.time()
    df = tools.add_durations(df)
    df = analysis.filter_df(df, 'time', one_week_prior, date='After')
    df = analysis.filter_df(df, 'time', today, date='Before')
    analysis.logfile_to_figure(df)
    print(time.time() - t)

def export_as_csv(df):
    df = tools.add_durations(df)
    df.to_csv('output.csv', index=False)
