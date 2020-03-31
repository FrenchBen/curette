# Import modules
from bs4 import BeautifulSoup
import requests, csv, unicodedata, sys, getopt, re
from firebase_admin import credentials
from firebase_admin import firestore

url = "https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfStandards/results.cfm"
json_data = {
    "organization":"",
    # "referencenumber":"6061", # working ref number
    "referencenumber":"",
    "recognitionnumber":"",
    "title":"",
    "category":"",
    "productcode":"",
    "regulationnumber":"",
    "effectivedatefrom":"",
    "effectivedateto":"",
    "sortcolumn":"st",
    "Search":"Search",
    "pagenum":"500",
    "start_search":"1"
    }

def fetchData(paging = 1):
    # set the paging index
    json_data["start_search"] = f"{paging}"

    # endpoint accepts POST and GET
    # r = requests.post(url, json=json_data)
    r = requests.get(url, params=json_data)
    
    print(f"Request: {r.url}")

    soup = BeautifulSoup(r.text, 'html.parser')
    return soup

def writeDB(table):
    # Use a service account
    cred = credentials.Certificate('path/to/serviceAccount.json')
    firebase_admin.initialize_app(cred)

    db = firestore.client()

def writeCSV(table):
    output_rows = []

    for table_row in table.findAll('tr')[1:]:
        #### TODO
        # deal with tr with tables inside
        # add support for href
        # dig into href data
        columns = table_row.findAll('td')
        output_row = []

        for column in columns:
            output_row.append(column.get_text(strip=True))
        output_rows.append(output_row)

    with open('output.csv', 'w') as csvfile:
        wr = csv.writer(csvfile)
        for output_row in output_rows:
            # print(f"Rows: {output_row}")
            try:
                wr.writerow(output_row)
                # wr.writerows(output_rows)
            except TypeError as e:
                print(f"Cannot write row: {output_row} - {e}")
                sys.exit(1)

def main(argv):
    # Set the ref data passed
    if (len(argv) > 0):
        opts, args = getopt.getopt(argv, 'r:p:',['reference-number=','pagenum='])
        for o, a in opts:
            if o in ('-r', '--reference-number'):
                json_data["referencenumber"] = f"{a}"
            elif o in ('-p', '--pagenum'):
                json_data["pagenum"] = f"{a}"
    
    soup = fetchData()
    table = soup.find(id="stds-results-table")
    # show the table content
    # print(table)
    if table == None:
        print(f"Device ID: {json_data['referencenumber']} does not exist")
        return
    
    # Todo: add proper paging - #user_provided
    txt_results = soup.find(id="stds-results-number").get_text(strip=True)
    matched = re.match(r'\d+ to \d+ of (\d+) Results', txt_results)

    if matched:
        print(f'Results found: {matched.group(1)}')
        total_results = matched.group(1)
    
    writeCSV(table)
    
    for paging in range(501, int(total_results), 500):
        soup = fetchData(paging)
        table = soup.find(id="stds-results-table")



if __name__ == "__main__":
   main(sys.argv[1:])