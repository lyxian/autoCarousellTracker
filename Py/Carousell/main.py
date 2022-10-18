import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.location.fromListing import getLocation
from datetime import datetime
from functools import reduce
import pandas as pd
import requests
import time
import pytz
import json
import re

def paginationHelper():
    return {
        'enforce': True,
        'fieldName': 'collections',
        'idsOrKeywords': { 'value': ['0'] }
    }

def requestPayload(query, querySize):

    return {
        'bestMatchEnabled': True,
        'canChangeKeyword': False,
        'count': querySize,
        'countryCode': 'SG',
        'countryId': '1880251',
        'filters': [paginationHelper() for _ in range(1)],
        'includeEducationBanner': True,
        'includeSuggestions': False,
        'locale': 'en',
        'query': query,
        "prefill": {},
        "sortParam": {},
    }

def searchCarousell(base_url_filter, payload):
    return requests.post(base_url_filter, json=payload).json()

def searchCarousell_cont(response, base_url_search, payload):
    temp = {
        'searchContext': response['data']['searchContext'],
        'session': response['data']['session'],
    }
    return requests.post(base_url_search, json=temp).json()

def searchResults(response):
    return [i['listingCard']['title'] for i in response['data']['results']]

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

def sortListingsFromResponse(response):
    return sorted([listing for listing in response['data']['results']], key=lambda x: x['listingCard']['overlayContent']['timestampContent']['seconds']['low'], reverse=True)

def allListings(response, query, num, keywords, base_url_search):
    columns_order = ['no.', 'timestamp', 'status', 'title',
                     'url', 'price (S$)', 'state', 'body', 'meetup', 'user', 'img']
    
    df = pd.DataFrame([listingInfo(i['listingCard']) for i in sortListingsFromResponse(response)])

    if keywords != ['']:
        # First Exclude
        df = df.loc[excludeListings(df, keywords), :]

        # Continue search till <num> reached
        response_1 = response
        while df.shape[0] < num:
            # print(df.shape[0])
            # base_url_search = 'https://www.carousell.sg/api-service/search/search/3.3/products/'
            response_1 = searchCarousell_cont(
                response_1, base_url_search, requestPayload(query, num))
            df_1 = pd.DataFrame([listingInfo(i['listingCard']) for i in sortListingsFromResponse(response_1)])
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
        resp = requests.get(base_url_listing).json()
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

if __name__ == '__main__':
    pass
