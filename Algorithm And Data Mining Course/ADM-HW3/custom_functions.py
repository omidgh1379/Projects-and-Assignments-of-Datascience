import pandas as pd
import json
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



# Function to download HTML from a URL with prefix and save it to a file
def crawler(url, output_path):
    full_url = 'https://www.findamasters.com/' + url
    try:
        response = requests.get(full_url)
        if response.status_code == 200:
            with open(output_path, 'w', encoding='utf-8') as html_file:
                html_file.write(response.text)
        else:
            print(f"Failed to download {full_url}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading {full_url}: {e}")



def parser(html_page):
    # Define your default values here
    default_values = {
    'courseName': None,
    'universityName': None,
    'facultyName': None,
    'isItFullTime': None,
    'description': None,
    'startDate': None,
    'fees': None,
    'modality': None,
    'duration': None,
    'city': None,
    'administration': None,
    'country': None,
    'url': None
}

    # Create a defaultdict with default values
    info = defaultdict(lambda: default_values)

   # Extract the text (HTML)
    with open(html_page, 'r', encoding='utf-8') as file:
        html_content = file.read()
    page_soup = BeautifulSoup(html_content, 'html.parser')

    # COURSE NAME
    page_links = page_soup.find_all('h1', {'class':'text-white course-header__course-title'})
    if page_links:
        first_h1_text = page_links[0].text
        info['courseName'] = str(first_h1_text)
    #else:
        # Handle the case when no 'h1' with 'data-permutive-title' is found
    #    print("No course name found.")
    #courseName = str(first_h1_text)

    # UNIVERSITY NAME
    # Extracting our tag of interest for the Name
    page_links = page_soup.find_all('a', {'class': 'course-header__institution'})
    # Extracting the name of the course as string and print it
    info['universityName'] = str(page_links[0].contents[0])

    # FACULTY NAME
    page_links = page_soup.find_all('a', {'class': 'course-header__department'})
    info['facultyName'] = str(page_links[0].contents[0])

    # FULL TIME
    page_links = page_soup.find_all('a', {'class': 'inheritFont'})
    info['isItFullTime'] = str(page_links[0].contents[0])

    # SHORT DESCRIPTION
    page_links = page_soup.find('div', {'id': 'Snippet'})
    info['description'] = str(page_links.get_text(separator='\n').strip())

    # STARTING DATE
    page_links = page_soup.find('span', {'class': 'key-info__start-date'})
    info['startDate'] = str(page_links.get_text())

    # FEES
    page_links = page_soup.find('a', {'class': 'noWrap inheritFont'})
    page_links = page_soup.find('div', {'class': 'course-sections__fees'})
    if page_links:
        fees_text = page_links.get_text(separator='\n').strip()
        # Remove "Fees" from the text content
        info['fees'] = fees_text.replace('Fees', '').strip()


    # MODALITY
    page_links = page_soup.find('span', {'class': 'key-info__content key-info__qualification py-2 pr-md-3 text-nowrap d-block d-md-inline-block'})
    # Get all elements within the span using find_all
    elementsWithinSpan = page_links.find_all('a')
    info['modality'] = ' '.join([element.text.strip() for element in elementsWithinSpan])

    # DURATION
    page_links = page_soup.find('span', {'class':'key-info__content key-info__duration py-2 pr-md-3 d-block d-md-inline-block'})
    info['duration']=str(page_links.text)

    # CITY
    page_links = page_soup.find('a', {'class':'card-badge text-wrap text-left badge badge-gray-200 p-2 m-1 font-weight-light course-data course-data__city'})
    info['city']=str(page_links.text)

    # ADMINISTRATION
    page_links = page_soup.find('span', {'class':'course-header__online-flag badge bg-white p-2 h6 shadow-sm mr-1'})
    if page_links == None:
        info['administration'] = "On Campus"
    else:
        info['administration']=str(page_links.text)

    # COUNTRY
    page_links = page_soup.find('a', {'class':'card-badge text-wrap text-left badge badge-gray-200 p-2 m-1 font-weight-light course-data course-data__country'})
    info['country']=page_links.text

    #URL
    page_links = page_soup.find('link')
    info['url'] = page_links.get('href')


    return(pd.DataFrame([info]))


        
def engine(query):
    """
    Given a query made up by multiple word it returns the documents were ALL the word are found
    """
    doc_set_indexes = []
    words_in_query = query.split()

    for word in words_in_query:
        # Stemming the word
        stemmed_word = stemmer.stem(word)

        # Check if the stemmed word exists in the 'Word' column after applying stemming
        if stemmed_word in vocabulary_reverse['Word'].apply(stemmer.stem).values:
            # Get the document set indexes for the stemmed word
            indexes_for_word = vocabulary_reverse[vocabulary_reverse['Word'].apply(lambda x: x == stemmed_word)]['reverse'].values

            # Flatten the lists in 'reverse' column
            flattened_indexes = [item for sublist in indexes_for_word for item in sublist]

            # Append the flattened document set indexes to the list
            doc_set_indexes.append(flattened_indexes)
           # print(doc_set_indexes)

        else:
            print(f"Stemmed word '{stemmed_word}' not found in vocabulary_reverse")

    # Find the intersection of all document sets
    selected_doc = list(set.intersection(*map(set, doc_set_indexes)))

    # Select rows using iloc
    selected_rows = df.iloc[selected_doc]

    return selected_rows
