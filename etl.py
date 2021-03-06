import os
import glob
import psycopg2
import pandas as pd
import numpy as np
from sql_queries import *
import warnings
warnings.filterwarnings('ignore')


def process_song_file(cur, filepath):
    '''
    This function read in json data from song_file filepath,
    prepare data, and call insert function to insert into song_table & artist_table.

            Parameters:
                    a (cur): conn.cursor(), an iterator fucntion that operates on db
                    b (filepath): file path to read in json data

            Returns:
                    No value returned
    '''
    # open song file
    df = pd.read_json(filepath, lines=True)

    # insert song record
    song_data = df.ix[0,:][['song_id', 'title', 'artist_id', 'year', 'duration']].values
    cur.execute(song_table_insert, song_data)

    # insert artist record
    df['artist_latitude'] = df['artist_latitude'].astype(str)
    df['artist_longitude'] = df['artist_longitude'].astype(str)
    artist_data = df.ix[0,:].loc[['artist_id', 'artist_name', 'artist_location',
                              'artist_latitude', 'artist_longitude']].values
    cur.execute(artist_table_insert, artist_data)


def process_log_file(cur, filepath):
    '''
    This function read in json data from log_file filepath,
    prepare data, and call insert function to insert into time_table & songplay_table.

            Parameters:
                    a (cur): conn.cursor(), an iterator fucntion that operates on db
                    b (filepath): file path to read in json data

            Returns:
                    No value returned
    '''
    # open log file
    df = pd.read_json(filepath, lines=True)

    # filter by NextSong action
    df = df[df['page']=='NextSong']

    # convert timestamp column to datetime
    t = pd.to_datetime(df['ts'])

    # insert time data records
    time_data = [t, t.dt.hour, t.dt.day, t.dt.week, t.dt.month, t.dt.year, t.dt.dayofweek]
    column_labels = ['start_time', 'hour', 'day', 'week', 'month', 'year', 'weekday']
    time_df = pd.DataFrame(dict(zip(column_labels, time_data)))

    for i, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))

    # load user table
    user_df = df[['userId', 'firstName', 'lastName', 'gender', 'level']]

    # insert user records
    for i, row in user_df.iterrows():
        cur.execute(user_table_insert, row)

    # insert songplay records
    for index, row in df.iterrows():

        # get songid and artistid from song and artist tables
        cur.execute(song_select, (row.song, row.artist, row.length))
        results = cur.fetchone()

        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None

        # insert songplay record
        songplay_data = np.array([pd.to_datetime(row.ts, unit='ms'),
                              row.userId, row.level, songid, artistid,
                     row.sessionId, row.location, row.userAgent])

        cur.execute(songplay_table_insert, songplay_data)


def process_data(cur, conn, filepath, func):
    '''
    This driver function is used to execute process_song_file & process_log_file
    on inidividual json files and insert into sql tables iteratively.

            Parameters:
                    a (cur): conn.cursor(), an iterator fucntion that operates on db
                    b (conn): Connection object that represents the database
                    c (filepath): file path to read in json data
                    d (func): function to call

            Returns:
                    No value returned
    '''
    # get all files matching extension from directory
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root,'*.json'))
        for f in files :
            all_files.append(os.path.abspath(f))

    # get total number of files found
    num_files = len(all_files)
    print('{} files found in {}'.format(num_files, filepath))

    # iterate over files and process
    for i, datafile in enumerate(all_files, 1):
        func(cur, datafile)
        conn.commit()
        print('{}/{} files processed.'.format(i, num_files))


def main():
    conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=student password=student")
    cur = conn.cursor()

    process_data(cur, conn, filepath='data/song_data', func=process_song_file)
    process_data(cur, conn, filepath='data/log_data', func=process_log_file)

    conn.close()


if __name__ == "__main__":

    # take care of the complain about numpy int64
    import numpy
    from psycopg2.extensions import register_adapter, AsIs

    def addapt_numpy_float64(numpy_float64):
        return AsIs(numpy_float64)
    def addapt_numpy_int64(numpy_int64):
        return AsIs(numpy_int64)
    register_adapter(numpy.float64, addapt_numpy_float64)
    register_adapter(numpy.int64, addapt_numpy_int64)

    main()
