import json
import schedule
import time
import shutil
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import datetime
import pandas as pd
import numpy as np
from argparse import ArgumentParser


def refresh_data(source_dir, local_dir):
    """

    Args:
        source_dir (Path):
        local_dir (Path):

    Returns:

    """
    print(f'Refreshing data from GDrive.')
    local = [x.name for x in local_dir.iterdir()]
    copied = 0
    for file in source_dir.iterdir():
        if file.name not in local:
            shutil.copy(file, local_dir)
            copied += 1
    print(f'Retrieved {copied} new files.')


def load_data(directory):
    """

    Args:
        directory (Path):

    Returns:
        pd.DataFrame
    """
    print(f'Loading data from local directory.')
    data = []
    for file in directory.iterdir():
        stem = file.stem
        date = datetime.datetime.strptime(stem, '%Y%m%d_%H%M')
        tmp = json.load(file.open())
        desired = tmp['Pt32Config']['DesiredTemp']
        actual = tmp['Pt32Config']['CurrentTemp']
        on = tmp['ComProtocolConfig']['IsOutputOn']
        data.append(dict(
            date=date,
            actual=actual,
            desired=desired,
            on=on
        ))

    return pd.DataFrame(data)


def plot_basic(data):
    """

    Args:
        data (pd.DataFrame):

    Returns:

    """
    print(f'Plotting data.')
    fig = make_subplots(rows=1, cols=1, specs=[[{'secondary_y': True}]])
    fig.add_scatter(x=data.date, y=data.desired, name='Desired', mode='markers+lines')
    fig.add_scatter(x=data.date, y=data.actual, name='Actual', mode='markers+lines')
    fig.add_scatter(x=data.date, y=data.on, name='Active', secondary_y=True, mode='markers+lines')
    return fig


def get_data_and_plot():
    print(f'Running at {datetime.datetime.now()}')
    gdrive_dir = Path('/mnt/GDrive_personal')
    source_dir = gdrive_dir / 'kotel_exports'
    local_dir = Path('./data')
    export_dir = Path('./exports')
    figure_export = export_dir / 'home_temp.html'

    refresh_data(source_dir=source_dir, local_dir=local_dir)
    data = load_data(local_dir).sort_values('date', ascending=True)
    fig = plot_basic(data)
    fig.write_html(figure_export)
    shutil.copy(figure_export, gdrive_dir)

    print(f'Done.\n')


def main():
    ap = ArgumentParser()
    ap.add_argument('--schedule', '-sch', default=False, action='store_true')
    args = ap.parse_args()
    
    if args.schedule:
        schedule.every(10).minutes.do(get_data_and_plot)
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        get_data_and_plot()


if __name__ == '__main__':
    main()
