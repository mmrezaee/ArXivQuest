from nltk.tokenize import sent_tokenize
from bs4.element import NavigableString, Tag

elements_of_interest = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p','table']

def correct_images_src(prefix,element):
    for img in element.find_all('img'):
        original_src = img['src']
        new_src = prefix+'/'+ original_src
        img['src'] = new_src

def extract_table(table):
    headers = [th.text.strip() for th in table.find_all('th')]
    rows = []
    for tr in table.find_all('tr'):
        cells = [td.text.strip() for td in tr.find_all(['td', 'th'])]
        rows.append(cells)
    return '\n'.join([' | '.join(headers)] + [' | '.join(row) for row in rows])

def extract_content(element):
    if isinstance(element, NavigableString):
        return str(element).strip()
    elif isinstance(element, Tag):
        if element.name == 'table':
            return extract_table(element)
        elif element.name in elements_of_interest:
            text_strip = element.text.strip()
            text_tokenize = sent_tokenize(text_strip)
            return '<sent>'.join(text_tokenize)
        else:
            all_sents = '<sent>'.join(filter(None, [extract_content(child) for child in element.children]))
            return all_sents
    return ''
