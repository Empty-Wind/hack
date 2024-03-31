import argparse
import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv

def fetch_google_search_results(query):
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = f"https://www.google.com/search?q={query}"
    response = requests.get(url, headers=headers)
    return response.text if response.status_code == 200 else None

def parse_search_results(html):
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    for g in soup.find_all('div', class_='tF2Cxc'):
        title = g.find('h3', class_='LC20lb MBeuO DKV0Md').text
        link = g.find('a')['href']
        results.append({'title': title, 'link': link})
    return results

def read_search_options(csv_file):
    with open(csv_file, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        return list(reader)  # Convert the DictReader object to a list

def save_results_to_excel(results, filename):
    df = pd.DataFrame(results)
    df.to_excel(filename, index=False)

# Command line argument parsing
parser = argparse.ArgumentParser()
parser.add_argument('-U', '--url', help="Target URL", required=True)
parser.add_argument('-C', '--csv', help="CSV file containing search options", required=True)
args = parser.parse_args()

# Reading search options from CSV
search_options = read_search_options(args.csv)

# Executing search for each row of options
for options in search_options:
    query_components = []
    intext = options.get('intext', '').lower()
    inurl = options.get('inurl', '').lower()
    filetype = options.get('filetype', '').lower()

    if intext and intext != 'null':
        query_components.append(f"intext:{intext}")
    if inurl and inurl != 'null':
        query_components.append(f"inurl:{inurl}")
    if filetype and filetype != 'null':
        query_components.append(f"filetype:{filetype}")

    query = f"site:{args.url} {' '.join(query_components)}"
    print(f"Searching for: {query}")
    html = fetch_google_search_results(query)
    if html:
        search_results = parse_search_results(html)
        if search_results:
            safe_filename = f"{'_'.join(query_components).replace(' ', '_')}.xlsx"
            save_results_to_excel(search_results, safe_filename)
            print(f"Saved {len(search_results)} results to {safe_filename}")
        else:
            print(f"No results found for query: {query}")
    else:
        print("Failed to fetch search results")
