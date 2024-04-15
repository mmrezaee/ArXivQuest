from nltk.tokenize import sent_tokenize
from bs4.element import NavigableString, Tag
import pandas as pd
import re


# Define elements of interest for content extraction
elements_of_interest = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p','table']


# Predefined model embedding dimensions for various models
MODEL_EMBEDDING_DIMENSIONS = {'all-MiniLM-L6-v2':384, 
                              'all-MiniLM-L12-v2':384,
                              'all-distilroberta-v1':768,
                              'all-mpnet-base-v2':768}
def correct_images_src(prefix,element):
    """
    Correct the source paths of <img> tags within an HTML (arXiv) element.

    Args:
        prefix (str): The URL prefix to prepend to image sources.
        element (Tag): The BeautifulSoup element containing <img> tags.
    """
    for img in element.find_all('img'):
        original_src = img['src']
        new_src = prefix+'/'+ original_src
        img['src'] = new_src


def pandas_extract_table(table):
    """
    Extracts a table from HTML and converts it into a Pandas DataFrame.

    Args:
        table (Tag): The BeautifulSoup tag representing the table.

    Returns:
        DataFrame: A DataFrame containing the table data.
    """
    # Extract headers from the table
    headers = [th.text.strip().lower() for th in table.find_all('th')]
    # Extract rows from the table
    rows = []
    for tr in table.find_all('tr')[1:]:  # Skip the header row for data rows
        cells = [td.text.strip().lower() for td in tr.find_all('td')]  # Use 'td' to avoid duplicating headers
        if cells:  # Ensure that the row is not empty
            rows.append(cells)
    # Create a DataFrame using the extracted data
    dataframe = pd.DataFrame(rows, columns=headers)
    return dataframe



def extract_table_as_string(table):
    """
    Extracts a table from HTML and converts it into a string representation.

    Args:
        table (Tag): The BeautifulSoup tag representing the table.

    Returns:
        str: A string representation of the table.
    """
    headers = [th.text.strip().lower() for th in table.find_all('th')]
    rows = []
    for tr in table.find_all('tr'):
        cells = [td.text.strip().lower() for td in tr.find_all(['td', 'th'])]
        rows.append(cells)
    table_string = '\n'.join([' | '.join(headers)] + [' | '.join(row) for row in rows])
    return table_string



def extract_content(element):
    """
    Recursively extracts and formats textual content from HTML elements.

    Args:
        element (NavigableString or Tag): The BeautifulSoup element to process.

    Returns:
        str: A string containing the processed text from the element.
    """
    if isinstance(element, NavigableString):
        return str(element).replace('\t',' ').replace('\n',' ').lower().strip()
    elif isinstance(element, Tag):
        if element.name == 'table':
            this_extracted_table= extract_table_as_string(element)
            return this_extracted_table
        elif element.name in elements_of_interest:
            text_strip = element.text.replace('\t',' ').replace('\n',' ').strip().lower()
            text_tokenize = sent_tokenize(text_strip)
            return '<sent>'.join(text_tokenize)
        else:
            all_sents = '<sent>'.join(filter(None, [extract_content(child) for child in element.children]))
            return all_sents
    return ''

