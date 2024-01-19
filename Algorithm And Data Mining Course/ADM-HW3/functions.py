import pandas as pd
import json
from datetime import datetime
from collections import defaultdict
from bs4 import BeautifulSoup
import requests
import os
import re
from collections import Counter
from functools import reduce
from tqdm.notebook import tqdm
from functools import reduce
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer
import heapq
from itertools import product
from geopy.geocoders import Nominatim
import folium
import geopy
from geopy import distance
from folium.plugins import HeatMap
import branca
import branca.colormap as cm
from PIL import Image
import ipywidgets as widgets
from IPython.display import display, Markdown
from nltk.tokenize import word_tokenize
import custom_functions


def extract_masters(this_url):
    result_url = requests.get(this_url)
    result_soup = BeautifulSoup(result_url.text, 'html.parser')
    result_links = result_soup.find_all('a', {'class': 'courseLink'})
    result_list = []
    for item in result_links:
        result_list.append(item['href'])
    return result_list



def parse_html(folder_path):
    # List all files in the folder
    files = os.listdir(folder_path)
    parsed_dfs = []
    # Iterate through all folders and subfolders using os.walk
    for folder_path, _, file_names in os.walk(folder_path):
        # Check if there are files in the current folder
        if file_names:
            # Iterate through each file in the current folder
            for file_name in file_names:
                file_path = os.path.join(folder_path, file_name)

                # Store the information only is the dictionary is not empty (has at list a name course)
                try:
                    # Parse the file and append the result to the list
                    parsed_df = custom_functions.parser(file_path)
                    parsed_dfs.append(parsed_df)
                except Exception as e:
                    # Print the file path when an exception occurs
                    print(f"Error parsing file: {file_path}")
                    # print(f"Error details: {e}")

    # Concatenate all DataFrames in the list
    concatenated_df = pd.concat(parsed_dfs, ignore_index=True)
    return concatenated_df


# Function to remove stopwords and punctuation from a text
def clean(text):
    """
    The following function returns the filtered element for each column of a dataframe.
    Filtering operation consists in removing punctuation and removing stopwords given text with lower case
    """
    words = word_tokenize(str(text))
    # Remove punctuation using NLTK and string.punctuation
    filtered_words = [word for word in words if word not in string.punctuation + "'’...?'+,-'‘“”„•…›✓"]
    # Remove stopwords
    filtered_words = [word for word in filtered_words if word.lower() not in stop_words]
    return ' '.join(filtered_words)



# Function to convert any currency to the common currency (USD in this case)
def convert_to_common_currency(target_currency='USD',currency_symbol = '£',amount=0):
    try:
        # Map the currency symbol to the API symbol
        api_currency_symbol = currency_symbol_mapping.get(currency_symbol)

        if not api_currency_symbol:
            return None

        # Extract the exchange rate from the pre-fetched rates
        exchange_rate = exchange_rates[api_currency_symbol]

        # Remove the currency symbol and commas, then convert to float
        amount = float(amount.replace(',', ''))

        # Convert to USD using the obtained exchange rate
        amount_target_currency = amount/(exchange_rate)
        return round(amount_target_currency,2)
        #return currency_symbol

    except Exception as e:
       return None


def return_cost(text):
    """
    return the maximum fees converted to USD given a text (description column)
    """
    # Return None if the input is not a string
    if not isinstance(text, str):
        return None  

    matches = re.finditer(pattern, text)
    converted_list = []

    for match in matches:
        value = match.group('value')
        if match.group('symbol_before'):
            symbol_before = match.group('symbol_before')
            # Combine symbol_before, value, and symbol_after into a single string
            converted_list.append(functions.convert_to_common_currency(currency_symbol = symbol_before,amount=value.replace(',','')))

        elif match.group('symbol_after'):
            symbol_after = match.group('symbol_after')
            converted_list.append(functions.convert_to_common_currency(currency_symbol= symbol_after,amount=value.replace(',','')))

    # Drop None values using a list comprehension
    if len(converted_list)>=1:
        filtered_list = [value for value in converted_list if value is not None]
        if len(filtered_list)>=1:
            return(max(filtered_list))


def rank_documents(query1):
    """
    Given a query, computes the tfidf for that query and evaluate the cosine similarity con for query given
    the document extracted with engine function. Returns the top-k documents
    """
    ## COMPUTING THE TFIDF FOR THE QUERY

   # Tokenize the query and save the stammed words for computinf tfidf
    tokens = word_tokenize(query1)
    stemmed_tokens = [stemmer.stem(word) for word in tokens]
    tfidf_vectorizer = TfidfVectorizer()

    # Combine the stemmed tokens considering it single string (document)
    stemmed_query = ' '.join(stemmed_tokens)

    # Fit the vectorizer on the list of queries and transform the query into a tfidf vector
    query_tfidf = tfidf_vectorizer.fit_transform([stemmed_query])

    # Convert the TF-IDF matrix to a dense pandas DataFrame
    tfidf_query = pd.DataFrame(query_tfidf.todense(), index=['query'], columns=tfidf_vectorizer.get_feature_names_out())

    ## OBTAINE THE TFIDF BEWTEEN THE QUERY AND THE DOCUMENT
    # Initialize a heap for the k-top results
    k_top_results = []

    # Iterate over the documents
    for idx, document_text in enumerate(functions.engine(query1)['description']):

        for index, tfidf in inverted_index_2['air']:
            if index in functions.engine('air pollution')['description'].index:
                print('nel documento',{index}, 'la cosine similarity e',tfidf)
        # Compute cosine similarity between the query and the document
        similarity_score = cosine_similarity(tfidf_query, tfidf_document)[0, 0]

       ## USING A HEAP TO HAVE THE TOP-K DOCUMENTS
        # Append the similarity score and document index to the k_top_results list
        k_top_results.append((round(similarity_score,5), functions.engine(query1)['description'].index[idx]))


    # Retrieve the k-top results from the heap using nlargest
    k_top_results = heapq.nlargest(10, k_top_results, key=lambda x: x[0])
    rank_df = pd.DataFrame()

    for cossim, indexsorted in k_top_results:
        # Return the information about the document sorted by cosine similarity
            document_info = df_query.loc[[indexsorted]].copy()
#            return document_info
            document_info['Similarity'] = cossim
            rank_df = pd.concat([rank_df, document_info])

    # Eventually we could reset the index of the final DataFrame
    # rank_df = rank_df.reset_index(drop=True)

    return rank_df


def rank_documents_advanced(query1,max_fees):
    """
    Given a query, computes the tfidf for that query and evaluate the cosine similarity con for query given
    the document extracting with engine function. Returns the top-k documents
    """

    central_point = input("In which city would you prefer to study?")
    max_distance = int(input("What is the maximum distance from the university to the city centre (in Kilometres) that you are willing to accept?"))
    student_point = geolocator.geocode(central_point) #get coordinates
    student_coordinates = [student_point.latitude, student_point.longitude] #add the coordinates to a list

    #define the epsilon value for the new metric, so that the score is never zero
    epsilon = 0.05


    ## COMPUTING THE IFIDF FOR THE QUERY
    # Tokenize the query and save the stammed words for computinf tfidf
    tokens = word_tokenize(query1)
    stemmed_tokens = [stemmer.stem(word) for word in tokens]
    tfidf_vectorizer = TfidfVectorizer()

    # Combine the stemmed tokens considering it single string (document)
    stemmed_query = ' '.join(stemmed_tokens)

    # Fit the vectorizer on the list of queries and transform the query into a tfidf vector
    query_tfidf = tfidf_vectorizer.fit_transform([stemmed_query])

    # Convert the TF-IDF matrix to a dense pandas DataFrame
    tfidf_query = pd.DataFrame(query_tfidf.todense(), index=['query'], columns=tfidf_vectorizer.get_feature_names_out())

    ## OBTAINE THE TFIDF BEWTEEN THE QUERY AND THE DOCUMENT
    # Initialize a heap for the k-top results
    k_top_results = []

    # Iterate over the documents
    for idx, document_text in enumerate(engine(query1)['description']):

        # Tokenize and preprocess the document text
        document_tokens = [stemmer.stem(word) for word in word_tokenize(document_text)]
        document_text_processed = ' '.join(document_tokens)

        # Transform the document text using the fitted vectorizer
        tfidf_document = tfidf_vectorizer.transform([document_text_processed])



        uni_name_info = df_query.loc[[idx]].copy()
        univ = uni_name_info["universityName"][idx] #get the university name
        uni_fees = raw_fees['fees (USD)'][idx] #get the fees


        uni_point = geolocator.geocode(univ) #get coordinates
        uni_coordinates = [uni_point.latitude, uni_point.longitude] #add the coordinates to a list
        #compute the distance between the university
        # and the student's specified location
        uni_distance = distance.distance(uni_coordinates,student_coordinates).km 

        print("The distance from your specified location is",round(uni_distance,2),"Km")


        #Compute the new score between the query and the document
        #print(uni_distance/max_distance)
        print("Uni_fees / Max_fees =", uni_fees/max_fees)
        print("Uni_fees =", uni_fees)
        similarity_score = (cosine_similarity(tfidf_query, tfidf_document)[0, 0])*(epsilon+1-(uni_distance/max_distance))*(epsilon+1-(uni_fees/max_fees))

        #Since the score has to be somewhat personal, we let the student decide the maximum distance 
        #from the university. if the distance is greater than the specified distance
        #the score will be negative. A negative score will not be one of the top choices.
        #The negative score is due to the fact that the second parenthesis is negative, since
        # the distance can be greater than the maximum distance, which is an input from the user

        print("Newmetric =",(epsilon + 1-(uni_distance/max_distance))*(epsilon + 1-(uni_fees/max_fees)))
        print(similarity_score)


       ## USING A HEAP TO HAVE THE TOP-K DOCUMENTS
        # Append the similarity score and document index to the k_top_results list
        k_top_results.append((round(similarity_score,5), engine(query1)['description'].index[idx]))


    # Retrieve the k-top results from the heap using nlargest
    k_top_results = heapq.nlargest(10, k_top_results, key=lambda x: x[0])
    rank_df = pd.DataFrame()

    for cossim, indexsorted in k_top_results:
        # Return the information about the document sorted by cosine similarity
            document_info = df_query.loc[[indexsorted]].copy()
            print(document_info.columns)
#            return document_info
            document_info['Similarity'] = cossim
            rank_df = pd.concat([rank_df, document_info])

    # Eventually we could reset the index of the final DataFrame
    # rank_df = rank_df.reset_index(drop=True)

    return rank_df



def create_widgets():

    # Dropdown menu widget

    course_name_widget = widgets.Text(description='Course Name:')
    university_name_widget = widgets.Text(description='University Name:')
    cities= sorted(df1['city'].unique().tolist())
    university_city_widget = widgets.Dropdown(options=['--']+cities, description='University Cities:')
    country= sorted(df1['country'].unique().tolist())
    university_country_widget = widgets.Dropdown(options=country, description='University Country:')

    # FloatRangeSlider for fee range
    fee_range_widget = widgets.FloatRangeSlider(
        min=df1[df1['fees (USD)'].notna()]['fees (USD)'].min(),
        max=df1[df1['fees (USD)'].notna()]['fees (USD)'].max(),
        step=100,
        description='Fee Range:'
    )

    # Selecting multiple countries
    # Get unique countries from the DataFrame
    all_countries= sorted(df1['country'].unique().tolist())

    # Dropdown widget allowing multiple country selections
    multi_select_dropdown = widgets.SelectMultiple(
        options=country,
        value=[country[0]],
        description='Select Countries:'
    )

    # Global variable to store selected countries
    selected_countries = set()

    # Dropdown widget allowing multiple country selections
    multi_select_dropdown = widgets.SelectMultiple(
        options=all_countries,
        value=[all_countries[0]],
        description='Select Countries:'
    )


    # Checkbox widgets
    started_courses_widget = widgets.Checkbox(value=False, description='Started Courses')
    online_modality_widget = widgets.Checkbox(value=False, description='Online Modality')


    # Adjusting widget layout for better readability
    course_name_widget.style.description_width = '40%'
    university_name_widget.style.description_width= '40%'
    university_city_widget.style.description_width= '40%'
    multi_select_dropdown.style.description_width = '40%'


    # Adjusting widget layout for better readability
    fee_range_widget.layout.width = '50%'


    # Display widgets
    display(course_name_widget, university_name_widget,university_city_widget,
            multi_select_dropdown, fee_range_widget, started_courses_widget, online_modality_widget)


    # Function to handle widget value change
    def on_multi_select_change(change):
        global selected_countries
        selected_countries.update(change.new)

        display(Markdown(f'You selected {selected_countries}'))

    # Attach the function to the widget's value change event
    multi_select_dropdown.observe(on_multi_select_change, names='value')



#-------------------------------------------
# Mapping of month names to their numerical values
month_mapping = {
'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
, ' January': 1, ' February': 2, ' March': 3, ' April': 4, ' May': 5, ' June': 6,
' July': 7, ' August': 8, ' September': 9, ' October': 10, ' November': 11, ' December': 12
}


# Function to perform actions based on selected values
def extract_multiple_query(q):
    global df2  # Declare df2 as a global variable

    df3 = df2.copy()
    ##COURSE NAME
    # Check if the word for the course are in the course name
    # Set case=False to be insentive to case
    if q[0] != '':
        result = df3['courseName'].str.contains(q[0], case=False)
        # Filtering the DataFrame based on the result
        df3 = df3[result]

    ##UNIVERSITY NAME
    # Check if the word for the course are in the course name
    # Set case=False to be insentive to case
    if q[1] != '':
        result1 = df3['universityName'].str.contains(q[1], case=False)
        # Filtering the DataFrame based on the result
        df3 = df3[result1]

    # CITY AND COUNTRY
    if q[2]=='--':
        pass
    elif not q[3]:
        pass
    else:
        df3 = df3[(df3['city'] == q[2]) | df3['country'].isin(q[3])]


    # (NON)-STARTED COURSES
    # Get the current month
    current_month = datetime.now().month

    # For each row save in is_before if exists a course that will start
    for index, row in df3.iterrows():
        months = row['startDate']

        # Keeping rows where i don't have information
        if 'See Course' in months:
            continue
        if 'Any Month' in months:
            continue

        # Initialize max_start_month before the if statement
        max_start_month = 0

        # Mapping the month in the number to make comparison when a course start in a single months
        if len(months) == 1:
            starting_month = month_mapping.get(months[0], 0)

            # If q[5] is False, indicating non-started courses
            if (current_month <= starting_month) and q[5]:
                df3 = df3.loc[[index]]
            elif q[5] == False:
                df3 = df3.loc[~(df3.index == index)]

        # Search the latest begin of course when has multiple start
        elif len(months) > 1:
            l=[]
            # Taking the latest months were a course starts
            mapped_months = [month_mapping.get(elem) for elem in months if pd.notna(elem)]
            for start_month in mapped_months:
                if pd.notna(start_month):  # Skip NaN values
                    if 9 <= start_month < current_month:
                        l.append(True)
                    elif 1 <= start_month <= 7+ current_month:
                        l.append(False)
            if False in l:
                if not q[5]:  # If q[5] is False, indicating non-started courses
                    continue
                else:
                    #print('index',index)
                    df3 = df3.loc[~(df3.index == index)]

    # FEES RANGE
    for index, row in df2.iterrows():
        fees = row['fees (USD)']
        condition = (fees < q[4][1]) and (fees > q[4][0]) and (pd.isna(fees))
        # Check if DataFrame is not empty before filtering
        if not df3.empty:
            df3 = df3[df3['fees (USD)'].apply(lambda x: (x < q[4][1]) or (x > q[4][0]) or pd.isna(x))]

    ## ONLINE/ ON CAMPUS
    # Filtering only online of on campus courses
    if  q[6] ==True:
        df3 = df3[df3['administration']=='Online']
    elif q[6]==False:
        df3 = df3[df3['administration']=='On Campus']

    if not df3.empty:
        return df3[['courseName', 'universityName','url']]
    else:
        print("Try a more flexible query. Your search did not produce any result")



def rank_documents1(query_advanced):
    """
    Given a query, computes the tfidf for that query and evaluate the cosine similarity con for query given
    the document extracting with engine function. Returns the top-k documents
    """
    ## COMPUTING THE IFIDF FOR THE QUERY

   # Tokenize the query and save the stammed words for computinf tfidf
    tokens = word_tokenize(query_advanced)
    stemmed_tokens = [stemmer.stem(word) for word in tokens]
    tfidf_vectorizer = TfidfVectorizer()

    # Combine the stemmed tokens considering it single string (document)
    stemmed_query = ' '.join(stemmed_tokens)

    # Fit the vectorizer on the list of queries and transform the query into a tfidf vector
    query_tfidf = tfidf_vectorizer.fit_transform([stemmed_query])

    # Convert the TF-IDF matrix to a dense pandas DataFrame
    tfidf_query = pd.DataFrame(query_tfidf.todense(), index=['query'], columns=tfidf_vectorizer.get_feature_names_out())

    ## OBTAINE THE TFIDF BEWTEEN THE QUERY AND THE DOCUMENT
    # Initialize a heap for the k-top results
    k_top_results = []

    # Iterate over the documents
    for idx, document_text in enumerate(engine(query_advanced)['description']):

        # Tokenize and preprocess the document text
        document_tokens = [stemmer.stem(word) for word in word_tokenize(document_text)]
        document_text_processed = ' '.join(document_tokens)

        # Transform the document text using the fitted vectorizer
        tfidf_document = tfidf_vectorizer.transform([document_text_processed])

        # Compute cosine similarity between the query and the document
        similarity_score = cosine_similarity(tfidf_query, tfidf_document)[0, 0]

        # Display the cosine similarity score
        #print("Cosine Similarity Score:", similarity_score,idx)

       ## USING A HEAP TO HAVE THE TOP-K DOCUMENTS
        # Append the similarity score and document index to the k_top_results list
        k_top_results.append((round(similarity_score,5), engine(query_advanced)['description'].index[idx]))


    # Retrieve the k-top results from the heap using nlargest
    k_top_results = heapq.nlargest(10, k_top_results, key=lambda x: x[0])
    rank_df = pd.DataFrame()

    for cossim, indexsorted in k_top_results:
        # Return the information about the document sorted by cosine similarity
            document_info = df_query.loc[[indexsorted]].copy()
#            return document_info
            document_info['Similarity'] = cossim
            rank_df = pd.concat([rank_df, document_info])

    # Eventually we could reset the index of the final DataFrame
    # rank_df = rank_df.reset_index(drop=True)

    return rank_df
