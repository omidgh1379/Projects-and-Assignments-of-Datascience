# Libraries
from collections import Counter
import pandas as pd


# Extracting features functions

# Returns a dataframe containing user_id and its average_watch_duration
def get_average_click_duration(df):
    result_df = df.groupby("user_id")["duration"].mean().reset_index()
    return result_df.rename(columns={'duration': 'average_click_duration'})


# Returns a dataframe containing user_id and the most common genre in its watched shows
def get_favorite_genre(df):
    # Remove zapping cases
    df = df.drop(df[df.duration == 0].index)

    # Group by user_id and aggregate genres as a list of lists
    grouped_df = df.groupby('user_id')['genres'].agg(list).reset_index()

    def get_most_common_genre_for_user(list_of_lists):

        # Flatten the list of genres of each user, removing the "NOT AVAILABLE" cases
        flat_genre_list = [item for sublist in list_of_lists for item in sublist if item != "NOT AVAILABLE"]

        # Return the most present genre or None
        if len(flat_genre_list) > 0:
            return Counter(flat_genre_list).most_common(1)[0][0]
        else:
            return None

    # Find the most common genre for each user
    grouped_df['favorite_genre'] = grouped_df['genres'].apply(lambda x: get_most_common_genre_for_user(x))

    # Return the result
    result_df = grouped_df[['user_id', 'favorite_genre']]
    return result_df


# Returns a dataframe containing user_id and the time of the day (Morning/Afternoon/Night)
# when the user spends the most time on the platform
def get_favorite_login_time(df):
    # Group by user_id and time_of_day and sum durations
    grouped_df = df.groupby(['user_id', 'time_of_day'])['duration'].sum().reset_index()

    # Find the index of the maximum total duration for each user
    idx_max = grouped_df.groupby('user_id')['duration'].idxmax()

    # Use the indices to get the corresponding time_of_day values
    result_df = grouped_df.loc[idx_max, ['user_id', 'time_of_day', 'duration']]

    # Remove duration column
    result_df = result_df.drop("duration", axis=1)

    # Rename and return
    return result_df.rename(columns={'time_of_day': 'favorite_time_of_day'})


# Returns a dataframe containing user_id and its tendency to old or recent shows
def get_old_or_recent_shows_preference(df):
    # Remove zapping cases
    df = df.drop(df[df.duration == 0].index)

    # Group by user_id and aggregate movie release years as a list
    grouped_df = df.groupby('user_id')['release_date'].agg(lambda x: list(x.dt.year)).reset_index()

    # Categorize user preference based on the sum of years greater than 2010
    grouped_df["show_preference"] = grouped_df["release_date"].apply(
        lambda x: "Recent shows" if sum([year > 2010 for year in x]) > (len(x) / 2) else "Old shows")

    # Return the result
    return grouped_df[['user_id', 'show_preference']]


# Returns a dataframe containing user_id and its average_click_duration_per_day
def get_average_click_duration_per_day(df):
    # Group by user_id and date, then calculate the total duration per day
    grouped_df = df.groupby(['user_id', df['datetime'].dt.date])['duration'].sum().reset_index()

    # Group by user_id and calculate the mean duration across all days
    result_df = grouped_df.groupby("user_id")["duration"].mean().reset_index()

    # Rename and return
    return result_df.rename(columns={'duration': 'average_time_per_day'})


# -----------------------------------------------------------------------------------------------------------------

# Returns a dataframe containing user_id and its total number of clicks
def get_number_of_logins(df):
    return df.groupby('user_id')['datetime'].count().reset_index(name='total_number_of_clicks')


# Returns a dataframe containing user_id and the monthly average number of unique shows watched
def average_shows_count_per_month(df):
    # Remove zapping cases
    df = df.drop(df[df.duration == 0].index)

    # Create month column
    df['month'] = df['datetime'].dt.month

    # Group by user_id and month and count the number of unique shows
    grouped_df = df.groupby(['user_id', 'month'])['movie_id'].nunique()

    # Return the mean
    return grouped_df.groupby('user_id').mean().reset_index(name='average_shows_count_per_month')


# Returns a dataframe containing for each user_id the rate between shows watched during weekends and total shows watched
def percentage_shows_watched_in_weekends(df):
    # Remove zapping cases
    df = df.drop(df[df.duration == 0].index)

    # Create a column indicating working_day or weekend
    df['day_of_week'] = df['datetime'].dt.dayofweek
    df['day_type'] = df['day_of_week'].apply(lambda x: 'working_day' if x < 5 else 'weekend')

    # Count the number of films both on working days and weekends
    grouped_df = df.groupby(['user_id', 'day_type'])['movie_id'].nunique().unstack(fill_value=0).reset_index()

    # Calculate the rate of films on weekends / total films watched
    grouped_df['weekend_rate'] = grouped_df['weekend'] / (grouped_df['weekend'] + grouped_df['working_day'])

    return grouped_df[['user_id', 'weekend_rate']]


# Returns a dataframe containing for each user_id the count of shows watched during uk holidays
def count_films_watched_in_holidays(df):
    # Remove zapping cases
    df = df.drop(df[df.duration == 0].index)

    # Get month and day
    df['date'] = df['datetime'].dt.strftime('%m-%d')

    # Define UK holidays without the year
    uk_holidays = [
        '01-01',  # New Year's Day
        '12-25',  # Christmas Day
        '12-26',  # Boxing Day
        '04-02',  # Good Friday
        '04-05',  # Easter Monday
        '05-03',  # Early May Bank Holiday
        '05-31',  # Spring Bank Holiday
        '08-30',  # Late Summer Bank Holiday
    ]

    # Create a column indicating whether each date is in a UK holiday
    df['holiday_status'] = df['date'].apply(lambda x: 'holiday' if x in uk_holidays else 'not_holiday')

    # Count the number of films both on not holidays and holidays
    grouped_df = df.groupby(['user_id', 'holiday_status'])['movie_id'].nunique().unstack(fill_value=0).reset_index()

    # Take just the holidays one
    grouped_df['holidays_shows_count'] = grouped_df['holiday']

    return grouped_df[['user_id', 'holidays_shows_count']]


# Returns a dataframe containing for each user the average release time of watched shows
def average_release_date(df):
    # Remove zapping cases
    df = df.drop(df[df.duration == 0].index)

    # Compute average release date and return
    return df.groupby('user_id')['release_date'].mean().dt.year.reset_index(name='average_release_date')


# Returns a dataframe containing for each user the rate between zapping clicks and total clicks
def zapping_rate(df):
    # Count the number of times duration is 0 within each user group
    zero_duration_counts = df[df['duration'] == 0].groupby('user_id')['duration'].count().reset_index(
        name='zero_duration_count')

    # Count the total number of elements in each user group
    total_counts = df.groupby('user_id')['duration'].count().reset_index(name='total_count')

    # Merge the two DataFrames on 'user_id'
    merged_df = pd.merge(zero_duration_counts, total_counts, on='user_id', how='right')

    # Calculate the ratio of zero duration count to the total count
    merged_df['zapping_rate'] = merged_df['zero_duration_count'] / merged_df['total_count']

    # Fill NaN values with 0 (in case there are no zero durations for some users)
    merged_df['zapping_rate'] = merged_df['zapping_rate'].fillna(0)

    return merged_df[['user_id', 'zapping_rate']]


# Returns a dataframe containing for each user a measure of sparsity of genres
def get_genre_variance(df):
    # Remove zapping cases
    df = df.drop(df[df.duration == 0].index)

    # Group by user_id and aggregate genres as a list of lists
    grouped_df = df.groupby('user_id')['genres'].agg(list).reset_index()

    def get_genre_sparsity_for_user(list_of_lists):

        # Flatten the list of genres of each user, removing the "NOT AVAILABLE" cases
        flat_genre_list = [item for sublist in list_of_lists for item in sublist if item != "NOT AVAILABLE"]

        # Return number of different genres / total shows or None
        if len(flat_genre_list) > 0:
            return len(set(flat_genre_list)) / len(flat_genre_list)
        else:
            return None

    # Get genre sparsity for each user
    grouped_df['genre_sparsity'] = grouped_df['genres'].apply(lambda x: get_genre_sparsity_for_user(x))

    # Return the result
    result_df = grouped_df[['user_id', 'genre_sparsity']]
    return result_df


# Returns a dataframe containing for each user the number of unique watched shows
def unique_movies_watched(df):
    # Remove zapping cases
    df = df.drop(df[df.duration == 0].index)

    return df.groupby('user_id')['movie_id'].nunique().reset_index(name='unique_movies_watched')


# Returns a dataframe containing for each user the average time difference between movie release and watch date
def average_time_difference(df):
    # Remove zapping cases
    df = df.drop(df[df.duration == 0].index)

    # Calculate the time difference in days between release_date and datetime
    df['time_difference'] = (df['datetime'] - df['release_date']).dt.days

    # Group by user_id and calculate the average time difference
    result_df = df.groupby('user_id')['time_difference'].mean().reset_index(name='average_time_difference')

    return result_df


# Returns a dataframe containing for each user the season with the highest total duration
def highest_duration_season(df):
    # Remove zapping cases
    df = df.drop(df[df.duration == 0].index)

    # Extract the season from the datetime column
    df['season'] = df['datetime'].dt.month % 12 // 3 + 1

    # Group by user_id and season, sum the durations
    grouped_df = df.groupby(['user_id', 'season'])['duration'].sum().reset_index()

    # Find the season with the maximum total duration for each user
    idx_max = grouped_df.groupby('user_id')['duration'].idxmax()
    result_df = grouped_df.loc[idx_max, ['user_id', 'season', 'duration']]

    # Remove duration column
    result_df = result_df.drop("duration", axis=1)

    # Rename and return
    return result_df.rename(columns={'season': 'highest_duration_season'})


# Dictionary used to reduce from 24 genres to 4
genres_reduce = {'Thriller': 'Drama',
                 'Drama': 'Drama',
                 'Biography': 'Drama',
                 'Animation': 'Comedy',
                 'Documentary': 'Other',
                 'Horror': 'Drama',
                 'Comedy': 'Comedy',
                 'Adventure': 'Action',
                 'Action': 'Action',
                 'Short': 'Other',
                 'Sci-Fi': 'Action',
                 'Mystery': 'Action',
                 'Fantasy': 'Action',
                 'Crime': 'Action',
                 'Romance': 'Drama',
                 'Family': 'Other',
                 'Reality-TV': 'Other',
                 'War': 'Action',
                 'History': 'Drama',
                 'Western': 'Other',
                 'Talk-Show': 'Other',
                 'Sport': 'Other',
                 'Music': 'Other',
                 'Musical': 'Other'}
