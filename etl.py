import os
import glob
import psycopg2
import pandas as pd
from sql_queries import *


def process_song_file(cur, filepath):
    """
    This procedure processes a song file whose filepath has been provided as an arugment.
    It extracts the song information in order to store it into the songs table.
    Then it extracts the artist information in order to store it into the artists table.

    INPUTS:
    * cur the cursor variable
    * filepath the file path to the song file
    """
    # open song file
    df = pd.read_json(filepath,lines=True)
    song_list = ['song_id', 'title', 'artist_id', 'year', 'duration']
    # insert song record
    song_data = df[song_list].values[0].tolist()
    cur.execute(song_table_insert, song_data)
    
    # insert artist record
    artist_list = ['artist_id', 'artist_name', 'artist_location', 'artist_latitude', 'artist_longitude']
    artist_data = df[artist_list].values[0].tolist()
    cur.execute(artist_table_insert, artist_data)


def process_log_file(cur, filepath):
    """
    This procedure processes a log file whose filepath has been provided as an arugment.
    It extracts the log information in order to store it into the time table.
    After filtering for NextStong and conversion of timestamp columns it inserts time data to the table

    INPUTS:
    * cur the cursor variable
    * filepath the file path to the song file
    """
    # open log file
    df = pd.read_json(filepath, lines=True)

    # filter by NextSong action
    df = df.loc[df['page']=='NextSong']

    # convert timestamp column to datetime
    df['ts'] = df['ts'].apply(pd.to_datetime)
    t = df
    # insert time data records

    time_data = ([t['ts'], t['ts'].dt.hour, t['ts'].dt.day, t['ts'].dt.week, t['ts'].dt.month, t['ts'].dt.year,
                  t['ts'].dt.day_name()])
    column_labels = (['timestamp', 'hour', 'day', 'week_of_year', 'month', 'year', 'weekday'])
    time_df = pd.DataFrame(dict(zip(column_labels, time_data)))
    #time_df['timestamp'] = time_data['timestamp'].apply(pd.to_datetime)
    for i, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))

    # load user table
    user_col_list = ['userId', 'firstName', 'lastName', 'gender', 'level']
    user_df = df.filter(user_col_list)

    # insert user records
    for i, row in user_df.iterrows():
        cur.execute(user_table_insert, row)

    # insert songplay records
    for index, row in df.iterrows():
        
        # get songid and artistid from song and artist tables
        cur.execute(song_select, (row.song, row.artist,row.length))
        results = cur.fetchone()
        
        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None

        # insert songplay record
        songplay_data = ([row.ts, row.userId, row.level, songid, artistid, row.sessionId, row.location, row.userAgent])
        cur.execute(songplay_table_insert, songplay_data)


def process_data(cur, conn, filepath, func):
    """
    This procedure processes a log file whose filepath has been provided as an arugment.
    It extracts the log information in order to store it into the time table.
    After filtering for NextStong and conversion of timestamp columns it inserts time data to the table

    INPUTS:
    * cur the cursor variable
    * conn the connection variable
    * filepath the file path to the song file
    * func the function used to insert data
    """
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
    """
    This fucntion connects to database, extract and loads data from filepath into database
    """
    conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=student password=student")
    cur = conn.cursor()

    process_data(cur, conn, filepath='data/song_data', func=process_song_file)
    process_data(cur, conn, filepath='data/log_data', func=process_log_file)

    conn.close()


if __name__ == "__main__":
    main()