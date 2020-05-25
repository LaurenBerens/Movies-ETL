#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import json
import re
from sqlalchemy import create_engine
from config import db_password
import time


# In[2]:


try:
    #read in Kaggle movie csv
    kaggle_metadata = pd.read_csv('movies_metadata.csv', low_memory=False)
    ratings = pd.read_csv('ratings.csv')
    #read in wiki movie json
    file_dir = '/Users/lauren/Desktop/Class'
    with open(f'{file_dir}/wikipedia.movies.json', mode='r') as file:
        wiki_movies_raw = json.load(file)

except:
    Print("File load error.")


# In[3]:


#read in wiki movie json
file_dir = '/Users/lauren/Desktop/Class'


# In[4]:


with open(f'{file_dir}/wikipedia.movies.json', mode='r') as file:
    wiki_movies_raw = json.load(file)


# In[5]:


wiki_movies_df = pd.DataFrame(wiki_movies_raw)


# In[6]:


wiki_movies = [movie for movie in wiki_movies_raw
               if ('Director' in movie or 'Directed by' in movie)
                   and 'imdb_link' in movie
                   and 'No. of episodes' not in movie]


# In[7]:


#check to make sure the title key exists then add to the empty dictionary
def clean_movie(movie):
    movie = dict(movie) #create a non-destructive copy
    alt_titles = {}
    for key in ['Also known as','Arabic','Cantonese','Chinese','French',
                'Hangul','Hebrew','Hepburn','Japanese','Literally',
                'Mandarin','McCune–Reischauer','Original title','Polish',
                'Revised Romanization','Romanized','Russian',
                'Simplified','Traditional','Yiddish']:
        if key in movie:
            alt_titles[key] = movie[key]
            movie.pop(key)
    if len(alt_titles) > 0:
        movie['alt_titles'] = alt_titles

    #merge column names with duplicate data
    def change_column_name(old_name, new_name):
        if old_name in movie:
            movie[new_name] = movie.pop(old_name)
    #change other column names as well within the same function
    change_column_name('Adaptation by', 'Writer(s)')
    change_column_name('Country of origin', 'Country')
    change_column_name('Directed by', 'Director')
    change_column_name('Distributed by', 'Distributor')
    change_column_name('Edited by', 'Editor(s)')
    change_column_name('Length', 'Running time')
    change_column_name('Original release', 'Release date')
    change_column_name('Music by', 'Composer(s)')
    change_column_name('Produced by', 'Producer(s)')
    change_column_name('Producer', 'Producer(s)')
    change_column_name('Productioncompanies ', 'Production company(s)')
    change_column_name('Productioncompany ', 'Production company(s)')
    change_column_name('Released', 'Release Date')
    change_column_name('Release Date', 'Release date')
    change_column_name('Screen story by', 'Writer(s)')
    change_column_name('Screenplay by', 'Writer(s)')
    change_column_name('Story by', 'Writer(s)')
    change_column_name('Theme music composer', 'Composer(s)')
    change_column_name('Written by', 'Writer(s)')
    
    return movie  


# In[8]:


#list comprehension to make list of cleaned movies
clean_movies = [clean_movie(movie) for movie in wiki_movies]
wiki_movies_df = pd.DataFrame(clean_movies)


# In[9]:


wiki_movies_df = pd.DataFrame(clean_movies)


# In[10]:


#extract movie IDs
wiki_movies_df['imdb_id'] = wiki_movies_df['imdb_link'].str.extract(r'(tt\d{7})')


# In[11]:


#remove dup IDs
wiki_movies_df['imdb_id'] = wiki_movies_df['imdb_link'].str.extract(r'(tt\d{7})')
wiki_movies_df.drop_duplicates(subset='imdb_id', inplace=True)


# In[12]:


#remove
wiki_columns_to_keep = [column for column in wiki_movies_df.columns if wiki_movies_df[column].isnull().sum() < len(wiki_movies_df) * 0.9]
wiki_movies_df = wiki_movies_df[wiki_columns_to_keep]


# In[13]:


box_office = wiki_movies_df['Box office'].dropna() 


# In[14]:


#looking for columns without strings
def is_not_a_string(x):
    return type(x) != str
box_office[box_office.map(is_not_a_string)]


# In[15]:


#using a single function to figure out columns that are not a string
box_office[box_office.map(lambda x: type(x) != str)]


# In[16]:


box_office = box_office.apply(lambda x: ' '.join(x) if type(x) == list else x)


# In[17]:


#call up all of the box office numbers with 'million' or 'billion'
form_one = r'\$\s*\d+\.?\d*\s*[mb]illi?on'


# In[18]:


#call up all box office numbers with numbers and punctuation only
form_two = r'\$\s*\d{1,3}(?:[,\.]\d{3})+(?!\s[mb]illion)'


# In[19]:


#create variables for form_one and form_two to ID non-matching formats
matches_form_one = box_office.str.contains(form_one, flags=re.IGNORECASE)
matches_form_two = box_office.str.contains(form_two, flags=re.IGNORECASE)


# In[20]:


box_office = box_office.str.replace(r'\$.*[-—–](?![a-z])', '$', regex=True)


# In[21]:


def parse_dollars(s):
    # if s is not a string, return NaN
    if type(s) != str:
        return np.nan
    # if input is of the form $###.# million
    if re.match(r'\$\s*\d+\.?\d*\s*milli?on', s, flags=re.IGNORECASE):
        # remove dollar sign and " million"
        s = re.sub('\$|\s|[a-zA-Z]','', s)
        # convert to float and multiply by a million
        value = float(s) * 10**6
        # return value
        return value
    # if input is of the form $###.# billion
    elif re.match(r'\$\s*\d+\.?\d*\s*billi?on', s, flags=re.IGNORECASE):
        # remove dollar sign and " billion"
        s = re.sub('\$|\s|[a-zA-Z]','', s)
        # convert to float and multiply by a billion
        value = float(s) * 10**9
        # return value
        return value
    # if input is of the form $###,###,###
    elif re.match(r'\$\s*\d{1,3}(?:[,\.]\d{3})+(?!\s[mb]illion)', s, flags=re.IGNORECASE):
        # remove dollar sign and commas
        s = re.sub('\$|,','', s)
        # convert to float
        value = float(s)
        # return value
        return value
    # otherwise, return NaN
    else:
        return np.nan


# In[22]:


#extract values from box office
wiki_movies_df['box_office'] = box_office.str.extract(f'({form_one}|{form_two})', flags=re.IGNORECASE)[0].apply(parse_dollars)


# In[23]:


#drop box office column
wiki_movies_df.drop('Box office', axis=1, inplace=True)


# In[24]:


#crerate budget variable
budget = wiki_movies_df['Budget'].dropna()


# In[25]:


#convert list to strings
budget = budget.map(lambda x: ' '.join(x) if type(x) == list else x)


# In[26]:


#remove values between $ and -
budget = budget.str.replace(r'\$.*[-—–](?![a-z])', '$', regex=True)


# In[27]:


matches_form_one = budget.str.contains(form_one, flags=re.IGNORECASE)
matches_form_two = budget.str.contains(form_two, flags=re.IGNORECASE)


# In[28]:


#remove numbers within square brackets
budget = budget.str.replace(r'\[\d+\]\s*', '')


# In[29]:


#parse budget data
wiki_movies_df['budget'] = budget.str.extract(f'({form_one}|{form_two})', flags=re.IGNORECASE)[0].apply(parse_dollars)


# In[30]:


#drop original budget column
wiki_movies_df.drop('Budget', axis=1, inplace=True)


# In[31]:


#parse release date
release_date = wiki_movies_df['Release date'].dropna().apply(lambda x: ' '.join(x) if type(x) == list else x)


# In[32]:


#create functions to edit dates
date_form_one = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s[123]\d,\s\d{4}'
date_form_two = r'\d{4}.[01]\d.[123]\d'
date_form_three = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{4}'
date_form_four = r'\d{4}'


# In[33]:


release_date.str.extract(f'({date_form_one}|{date_form_two}|{date_form_three}|{date_form_four})', flags=re.IGNORECASE)


# In[34]:


wiki_movies_df['release_date'] = pd.to_datetime(release_date.str.extract(f'({date_form_one}|{date_form_two}|{date_form_three}|{date_form_four})')[0], infer_datetime_format=True)


# In[35]:


running_time = wiki_movies_df['Running time'].dropna().apply(lambda x: ' '.join(x) if type(x) == list else x)


# In[36]:


#uniform running time with "hours" in any form
running_time_extract = running_time.str.extract(r'(\d+)\s*ho?u?r?s?\s*(\d*)|(\d+)\s*m')


# In[37]:


#create DF with uniform running time
running_time_extract = running_time_extract.apply(lambda col: pd.to_numeric(col, errors='coerce')).fillna(0)


# In[38]:


#put run time into minutes
wiki_movies_df['running_time'] = running_time_extract.apply(lambda row: row[0]*60 + row[1] if row[2] == 0 else row[2], axis=1)


# In[39]:


#remove original running time column
wiki_movies_df.drop('Running time', axis=1, inplace=True)


# In[40]:


#keep rows that are F and drop original adult column
kaggle_metadata = kaggle_metadata[kaggle_metadata['adult'] == 'False'].drop('adult',axis='columns')


# In[41]:


kaggle_metadata['video'] == 'True'


# In[42]:


kaggle_metadata['video'] = kaggle_metadata['video'] == 'True'


# In[43]:


kaggle_metadata.shape


# In[44]:


kaggle_metadata['budget'] = kaggle_metadata['budget'].astype(int)
kaggle_metadata['id'] = pd.to_numeric(kaggle_metadata['id'], errors='raise')
kaggle_metadata['popularity'] = pd.to_numeric(kaggle_metadata['popularity'], errors='raise')


# In[45]:


# convert release date to pandas datetime function
kaggle_metadata['release_date'] = pd.to_datetime(kaggle_metadata['release_date'])


# In[46]:


#pull null on ratings
ratings.info(null_counts=True)


# In[47]:


pd.to_datetime(ratings['timestamp'], unit='s')


# In[48]:


ratings['timestamp'] = pd.to_datetime(ratings['timestamp'], unit='s')


# In[49]:


movies_df = pd.merge(wiki_movies_df, kaggle_metadata, on='imdb_id', suffixes=['_wiki','_kaggle'])


# In[50]:


#drop inaccurately merged data
movies_df = movies_df.drop(movies_df[(movies_df['release_date_wiki'] > '1996-01-01') & (movies_df['release_date_kaggle'] < '1965-01-01')].index)


# In[51]:


#drop nulls
movies_df[movies_df['release_date_wiki'].isnull()]


# In[52]:


#DROP Wiki: title, release date, AND language and production company(s) columns
movies_df.drop(columns=['title_wiki','release_date_wiki','Language'], inplace=True)


# In[53]:


#drop redundant data in paired up columns
def fill_missing_kaggle_data(df, kaggle_column, wiki_column):
    df[kaggle_column] = df.apply(
        lambda row: row[wiki_column] if row[kaggle_column] == 0 else row[kaggle_column]
        , axis=1)
    df.drop(columns=wiki_column, inplace=True)


# In[55]:


#reorder columns
movies_df = movies_df.loc[:, ['imdb_id','id','title_kaggle','original_title','tagline','belongs_to_collection','url','imdb_link',
                       'runtime','budget_kaggle','revenue','release_date_kaggle','popularity','vote_average','vote_count',
                       'genres','original_language','overview','spoken_languages','Country',
                       'production_companies','production_countries','Distributor',
                       'Producer(s)','Director','Starring','Cinematography','Editor(s)','Writer(s)','Composer(s)','Based on'
                      ]]


# In[56]:


#rename columns for consistency 
movies_df.rename({'id':'kaggle_id',
                  'title_kaggle':'title',
                  'url':'wikipedia_url',
                  'budget_kaggle':'budget',
                  'release_date_kaggle':'release_date',
                  'Country':'country',
                  'Distributor':'distributor',
                  'Producer(s)':'producers',
                  'Director':'director',
                  'Starring':'starring',
                  'Cinematography':'cinematography',
                  'Editor(s)':'editors',
                  'Writer(s)':'writers',
                  'Composer(s)':'composers',
                  'Based on':'based_on'
                 }, axis='columns', inplace=True)


# In[57]:


#pull out movieID and rating columns
rating_counts = ratings.groupby(['movieId','rating'], as_index=False).count()                 .rename({'userId':'count'}, axis=1)                 .pivot(index='movieId',columns='rating', values='count')


# In[58]:


#rename column
rating_counts.columns = ['rating_' + str(col) for col in rating_counts.columns]


# In[59]:


#left merge with ratings dataframe with uniformed movie_df
movies_with_ratings_df = pd.merge(movies_df, rating_counts, left_on='kaggle_id', right_index=True, how='left')


# In[60]:


#leave movies without ratings as blank not 0
movies_with_ratings_df[rating_counts.columns] = movies_with_ratings_df[rating_counts.columns].fillna(0)


# In[62]:


try:
    db_string = f"postgres://postgres:{db_password}@127.0.0.1:5432/Movies"
    engine = create_engine(db_string)
    movies_df.to_sql(name='movies', con=engine)
except: 
    print("Table failed to load to Postgres.")


# In[ ]:


#load ratings data in chunks
rows_imported = 0
#get the start_time from time.time()
start_time = time.time()
for data in pd.read_csv(f'ratings.csv', chunksize=1000000):
    print(f'importing rows {rows_imported} to {rows_imported + len(data)}...', end='')
    data.to_sql(name='ratings', con=engine, if_exists='append')
    rows_imported += len(data)

    # add elapsed time to final print out
    print(f'Done. {time.time() - start_time} total seconds elapsed')


# In[ ]:




