from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag

app = Flask(__name__)
def extract_table(table):
    headers = [th.text.strip() for th in table.find_all('th')]
    rows = []
    for tr in table.find_all('tr'):
        cells = [td.text.strip() for td in tr.find_all(['td', 'th'])]
        rows.append(cells)
    return '\n'.join([' | '.join(headers)] + [' | '.join(row) for row in rows])

# Route to serve the index.html page
@app.route('/')
def home():
    return render_template('index.html')

# Route to fetch content from a URL and highlight the abstract
@app.route('/fetch_content', methods=['POST'])
def fetch_content():
    print('fetch_content is called')
    url = request.json['url']
    response = requests.get(url)
    
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    #print(f'prettify: {soup.prettify}')
    elements_of_interest = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p','table']
# Assuming soup contains the BeautifulSoup object with the HTML content
    #abstract_div = soup.find('div', class_='ltx_abstract')
    # Find the abstract
    abstract_div = soup.find('div', class_='ltx_abstract')
    if abstract_div:
        abstract = abstract_div.find('p', class_='ltx_p')
        if abstract:
            # Apply a yellow background to the abstract for highlighting
            abstract['style'] = 'background-color: yellow;'
        else:
            return jsonify({"message": "Abstract paragraph not found"})
    else:
        return jsonify({"message": "Abstract div not found"})

    '''

# Function to recursively extract content
# Function to recursively extract content
    def extract_content(element):
        if isinstance(element, NavigableString):
            return str(element).strip()
        elif isinstance(element, Tag):
            if element.name == 'table':
                return extract_table(element)
            elif element.name in elements_of_interest:
                return f"{element.name.upper()}: {element.text.strip()}"
            else:
                return '\n'.join(filter(None, [extract_content(child) for child in element.children]))
        return ''

# Extract content from the main body of the document
    content = extract_content(soup.find('body'))
    print(f'content: {content}')
    # Find the abstract and highlight it (assuming 'abstract' is a correct identifier)
    introduction = soup.find('blockquote', class_='introduction')
    print(f'introduction is found: {introduction}')
    #print(f'**** soup from app.py: ****')
    #print(f'**** abstract is {abstract}****')
    if introduction:
        # Apply a yellow background to the abstract for highlighting
        introduction['style'] = 'background-color: yellow;'

    # Convert the soup object back to a string
    '''
    modified_html = str(soup)
    return jsonify({"content": modified_html})

if __name__ == '__main__':
    print('hellooooooo')
    app.run(debug=True)
