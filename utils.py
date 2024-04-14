from nltk.tokenize import sent_tokenize
from bs4.element import NavigableString, Tag
import pandas as pd

elements_of_interest = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p','table']

MODEL_EMBEDDING_DIMENSIONS = {'all-MiniLM-L6-v2':384, 
                              'all-MiniLM-L12-v2':384,
                              'all-distilroberta-v1':768,
                              'all-mpnet-base-v2':768}
def correct_images_src(prefix,element):
    for img in element.find_all('img'):
        original_src = img['src']
        new_src = prefix+'/'+ original_src
        img['src'] = new_src

def pandas_extract_table(table):
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

def extract_table(table):
    headers = [th.text.strip().lower() for th in table.find_all('th')]
    rows = []
    for tr in table.find_all('tr'):
        cells = [td.text.strip().lower() for td in tr.find_all(['td', 'th'])]
        rows.append(cells)
    #print(f'rows: {rows}, headers: {headers}')
    table_string = '\n'.join([' | '.join(headers)] + [' | '.join(row) for row in rows])
    #print(f'table_string: {table_string}')
    #table_dataframe = pd.DataFrame(rows, columns=headers)
    return table_string

#all_tables = []
def extract_content(element):
    if isinstance(element, NavigableString):
        return str(element).lower().strip()
    elif isinstance(element, Tag):
        if element.name == 'table':
            print('calling extract_table')
            this_extracted_table= extract_table(element)
            #all_tables.append(table_dataframe)
            #print(f'found table in {element}')
            #print(f'converted table is {this_extracted_table}')
            #print('*'*50)
            return this_extracted_table
        elif element.name in elements_of_interest:
            text_strip = element.text.strip().lower()
            text_tokenize = sent_tokenize(text_strip)
            return '<sent>'.join(text_tokenize)
        else:
            all_sents = '<sent>'.join(filter(None, [extract_content(child) for child in element.children]))
            return all_sents
    return ''

'''
with open('./temp_tables.txt','w') as file:
    for index,table in enumerate(all_tables):
        table_index = index+1
        file.write('\n')
        file.write('\n')
        file.write(f'index is {table_index}: ')
        file.write('\n')
        file.write(table)
        file.write('\n')
        file.write('*'*50)
        print(table)
        print('*'*50)
'''
