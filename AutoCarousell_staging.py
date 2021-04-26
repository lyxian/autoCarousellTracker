from datetime import datetime
from functools import reduce
import requests as r
import pandas as pd
import json
import pytz
import time
import ast  # literal_eval
import re

### GOOGLE SHEETS API ###
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import json
import os


def spreadSheetClient():
    scope = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        'client_secret.json', scope)
    client = gspread.authorize(creds)
    return client


def openWorkbook_key(client, key):
    return client.open_by_key(key)


def openWorkbook_name(client, name):
    return client.open(name)

## Workbook Methods ##
# add_worksheet( title , rows , cols )
# del_worksheet( <sheet> )
# duplicate_sheet( source_sheet_id , insert_sheet_index , new_sheet_id , new_sheet_name )
# values_clear( 'sheetname'!'range' )
# worksheets()


def newWorksheet(wb, query):
    last = len(wb.worksheets())
    try:
        return wb.duplicate_sheet(source_sheet_id=wb.sheet1.id, insert_sheet_index=last, new_sheet_name=query)
    except:
        sheet = [i for i in wb.worksheets() if i.title.lower()
                 == query.lower()][0]
        if sheet.get_all_records() == []:
            wb.del_worksheet(sheet)
            return wb.duplicate_sheet(source_sheet_id=wb.sheet1.id, insert_sheet_index=last, new_sheet_name=query)
        else:
            return sheet


def requestPayload(query: str, num: int) -> dict:
    return {
        "count": num,
        "countryCode": "SG",
        "countryId": "1880251",
        "filters": [],
        "isFreeItems": False,
        "locale": "en",
        "prefill": {"prefill_sort_by": ""},
        "query": query
    }


def searchCarousell(base_url_filter, payload):
    return r.post(base_url_filter, json=payload).json()


def searchCarousell_cont(response, base_url_search, payload):
    temp = {
        'searchContext': response['data']['searchContext'],
        'session': response['data']['session'],
    }
    return r.post(base_url_search, json=temp).json()
    payload_1 = payload.copy()
    payload_1.update(temp)
    return r.post(base_url_search, json=payload_1).json()


def searchResults(response):
    return [i['listingCard']['title'] for i in response['data']['results']]

# url > img > timestamp > title > price > body > state

from Py.utils.location.fromListing import getLocation

def listingInfo(result):
    temp = [i['stringContent'] for i in result['belowFold'][2:4]]
    temp = dict(zip(['body', 'state'], temp))
    timestamp = datetime.fromtimestamp(
        result['overlayContent']['timestampContent']['seconds']['low'], tz=pytz.timezone('Singapore'))
    #link = 'https://www.carousell.sg/p/' + re.sub(r'\W+', '-', result['title'] + '-').lower() + result['id']
    location_name, meetups = getLocation(result['id'])
    d = {
        'title': re.sub(r'\n', '', result['title']),
        'price (S$)': result['price'].split('$')[-1].replace(',', ''),
        'timestamp': datetime.strftime(timestamp, '%m-%d-%Y %I:%M %p'),
        'url': 'https://www.carousell.sg/p/' + result['id'],
        'img': result['photos'][0]['thumbnailUrl'],
        'user': result['seller']['username'],
        'status': '-',
        'meetup': '; '.join(meetups) if isinstance(meetups, list) else '-',
    }
    d.update(temp)
    return d


def allListings_depre(response):
    columns_order = ['no.', 'timestamp', 'status', 'title',
                     'url', 'price (S$)', 'state', 'body', 'user', 'img']
    df = pd.DataFrame([listingInfo(i['listingCard'])
                       for i in response['data']['results']])
    df['no.'] = [i for i in range(1, df.shape[0]+1)][::-1]
    return df[columns_order]


def allListings(response, query, num, keywords):
    columns_order = ['no.', 'timestamp', 'status', 'title',
                     'url', 'price (S$)', 'state', 'body', 'meetup', 'user', 'img']
    df = pd.DataFrame([listingInfo(i['listingCard'])
                       for i in response['data']['results']])
    if keywords != ['']:
        # First Exclude
        df = df.loc[excludeListings(df, keywords), :]

        # Continue search till <num> reached
        response_1 = response
        while df.shape[0] < num:
            # print(df.shape[0])
            base_url_search = 'https://www.carousell.sg/api-service/search/search/3.3/products/'
            response_1 = searchCarousell_cont(
                response_1, base_url_search, requestPayload(query, num))
            df_1 = pd.DataFrame([listingInfo(i['listingCard'])
                                 for i in response_1['data']['results']])
            df = df.append(df_1.loc[excludeListings(df_1, keywords), :])

        # Trim to <num> results
        df = df.iloc[:num, :]

    df['no.'] = [i for i in range(1, df.shape[0]+1)][::-1]
    return df[columns_order]


def excludeListings(df, keywords):
    ls = []
    for word in keywords:
        ls.append(df.loc[:, 'title'].apply(
            lambda x: word not in x.lower()).values)
    return [reduce(lambda x, y: x == y == True, i) for i in zip(*ls)]

# Return updated_df + last_index


def updatedListings(new_df, sheet):
    retry_times = len(sheet.get_all_records())
    # Empty Sheet
    if sheet.get_all_records() == []:
        return new_df, new_df.shape[0]
    # Locate Start Point
    else:
        new_df = new_df.reset_index(drop=True)
        records = sheet.get_all_records()
        urls = [rec['url'] for rec in records]
        for url in urls[:retry_times]:
            # Found
            if new_df.loc[new_df['url'] == url, :].shape[0] >= 1:
                new_count = new_df[new_df['url'] == url].index[-1]
                new_df = new_df.iloc[:new_count, :]
                # Update Index of "new_df"
                start = records[0]['no.'] + 1
                new_df.loc[:, 'no.'] = [
                    i for i in range(start, start+new_count)][::-1]
                # Add rest of records
                new_df = new_df.append(pd.DataFrame(records))
                return new_df, new_count

        # Push entire "new_df"
        start = records[0]['no.'] + 1
        new_df.loc[:, 'no.'] = [i for i in range(
            start, start+new_df.shape[0])][::-1]
        new_df = new_df.append(pd.DataFrame(records))
        return new_df, new_df.shape[0]


def sheetPayload(df):
    return [df.columns.tolist()] + df.values.tolist()

# Sheet > URLS > Status > Update (ALL)


def sheetStatus_all(sheet):    # Update Past Listings Every 8 Hours
    new_df = pd.DataFrame(sheet.get_all_values()[
                          1:], columns=sheet.get_all_values()[0])
    # Check for last updated row + Check Status
    urls = new_df.loc[new_df.loc[:, 'status'].apply(
        lambda x: x not in ['-', 'MIA', 'Sold']), 'url']

    if len(urls) != 0:
        #checkResults = [checkStatus([url[0], re.search(r'/p/(.*)', url[1]).group(1)]) for url in enumerate(urls)]
        checkResults = [checkStatus(
            re.search(r'/p/(.*)', url).group(1)) for url in urls]
        new_df.loc[new_df.loc[:, 'status'].apply(
            lambda x: x not in ['-', 'MIA', 'Sold']), 'status'] = checkResults
        sheet.update(sheetPayload(new_df))
        return f'{sheet.title} (all) : {len(checkResults)-len([i for i in checkResults if i == "-"])}/{len(checkResults)} listing status updated'
    else:
        return 'Already Updated'


def sheetStatus_new(sheet, num):    # Update '-' Every Hour
    new_df = pd.DataFrame(sheet.get_all_values()[
                          1:], columns=sheet.get_all_values()[0])
    # Check for last updated row + Check Status
    check_range = new_df.loc[:, 'status'] == '-'
    if num != 0:
        check_range[:num] = [False for _ in range(num)]
    urls = new_df.loc[check_range, 'url']

    if len(urls) != 0:
        #checkResults = [checkStatus([url[0], re.search(r'/p/(.*)', url[1]).group(1)]) for url in enumerate(urls)]
        checkResults = [checkStatus(
            re.search(r'/p/(.*)', url).group(1)) for url in urls]
        new_df.loc[check_range, 'status'] = checkResults
        sheet.update(sheetPayload(new_df))
        return f'{sheet.title} (new) : {len(checkResults)-len([i for i in checkResults if i == "-"])}/{len(checkResults)} listing status updated'
    else:
        return 'Already Updated'


def checkStatus(listing_id):
    base_url_listing = f'https://www.carousell.sg/api-service/listing/3.1/listings/{listing_id}/detail/'
    try:
        resp = r.get(base_url_listing).json()
    except:
        #print(f'{listing_id} [Failed]')
        return '-'
    if 'screens' in resp['data'].keys():
        if resp['data']['screens'][0]['ui_rules']['actions']['primary_button']['button_text'] == 'Sold':
            return 'Sold'
        elif resp['data']['screens'][0]['ui_rules']['actions']['primary_button']['button_text'] == 'Reserved':
            return 'Close'
        else:
            return 'Open'
    else:
        return 'MIA'


def showImage():
    from PIL import Image
    from io import BytesIO
    #img = Image.open(BytesIO(r.get(img_url).content))
    # display(img)
    pass

##### MAIN #####

# Open Workbook > Extract Data > Update Result > Update Listing Status (all -> new)


def start():
    check_interval = 3  # hours
    client = spreadSheetClient()
    wb = openWorkbook_name(client, 'Automated Carousell-Staging')

    base_url_filter = 'https://www.carousell.sg/api-service/filter/search/3.3/products/'
    settings_sheet = wb.worksheet('Settings')
    if len(settings_sheet.get_all_records()) == 0:
        return False, 'Stop'    # Stop Code <- No Settings
    else:
        settings = settings_sheet.get_all_records()

    live = settings[0]['Live']
    if live == 'FALSE':
        return False, 'Off'

    queries = [i['Query'].strip() for i in settings]
    excludes = [i['Exclude'] for i in settings]
    num = settings[0]['Number']
    delay = settings[0]['Delay (min)']
    settings[0]['Last Ran On'] = datetime.strftime(
        datetime.now(tz=pytz.timezone('Singapore')), '%Y/%m/%d %I:%M %p')
    # System Message
    print(
        f'{settings[0]["Last Ran On"]} : {queries} [Next Run in {delay} mins]')

    # Wait for Query
    if queries == []:
        return False, 'Wait'

    # Set Default "num"
    if num == '':
        num = 100

    # Set Default "delay"
    if delay == '':
        delay = 60

    checkedSheets = set()

    for query, exclude in zip(queries, excludes):
        if query != '':
            try:
                idx = queries.index(query)
                response = searchCarousell(
                    base_url_filter, requestPayload(query, num))
                df = allListings(response, query, num, list(
                    map(str.strip, exclude.split(','))))

                sheet = newWorksheet(wb, query)
                df, new_listings_num = updatedListings(df, sheet)
                sheet.update(sheetPayload(df))

                settings[idx]['Success'] = True
                settings[idx]['Error'] = '-'

                # Update Past-New Listings
                print(f'Updating (new) {sheet.title}...')
                print(sheetStatus_new(sheet, new_listings_num))
                checkedSheets.add(sheet.title)
            except Exception as e:
                settings[idx]['Success'] = False
                print(str(e))
                settings[idx]['Error'] = str(e)

    # Exclude First 2 Sheets
    sheetnames = [i.title for i in wb.worksheets()[2:]]

    # CheckSheet_new
    for sheetname in sheetnames:
        if sheetname not in checkedSheets:
            try:
                # Update Past-New Listings
                print(f'Updating {sheetname}...')
                print(sheetStatus_new(wb.worksheet(sheetname), 0))
            except Exception as e:
                print(e)
                pass

    # CheckSheet_all
    if datetime.now(tz=pytz.timezone('Singapore')).hour % check_interval == 0 and settings[0]['Updated'] == 'FALSE':
        for sheetname in sheetnames:
            try:
                print(f'Updating (all) {sheetname}...')
                print(sheetStatus_all(wb.worksheet(sheetname)))
                settings[0]['Updated'] = True
            except Exception as e:
                print(e)
                pass
    elif datetime.now(tz=pytz.timezone('Singapore')).hour % check_interval != 0:
        settings[0]['Updated'] = False

    try:
        settings[0]['Live'] = live
        settings_sheet.update(sheetPayload(pd.DataFrame(settings)))
    except:
        pass

    # Print Results
    if [i for i in settings if i['Error'] != '-']:    # Error
        return False, 'Fail'
    else:
        return True, delay


if __name__ == '__main__':
    while True:
        t_1 = time.perf_counter()
        success, cmd = start()
        print(success, cmd)
        break
        if success:
            print('Success')
            runtime = time.perf_counter() - t_1
            time.sleep(cmd*60 - runtime)
        else:
            if cmd == 'Stop':    # Stop Code
                print('Program Stopped...')
                break
            elif cmd == 'Wait':    # Wait 1 min
                print('Awaiting Query...')
                time.sleep(60)
            elif cmd == 'Off':
                print(
                    f'Sleeping since {datetime.strftime(datetime.now(tz=pytz.timezone("Singapore")),  "%Y-%m-%d %I:%M %p")}')
                time.sleep(10*60)
            else:    # Update Failed -> Stop with msg OR Retry in 1 min
                break
