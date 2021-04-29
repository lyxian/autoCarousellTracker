from flask import Flask, request
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Google.main import *
from Carousell.main import *
from utils.location.fromListing import getLocation
from datetime import datetime
from functools import reduce
import pandas as pd
import requests
import time
import pytz
import json
import re

def start(wb_name):
    check_interval = 3  # hours
    client = spreadSheetClient()
    wb = openWorkbook_name(client, wb_name)

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

# not required for WEB : PUBLIC_URL + cmd
def hostServer(wb_name='Automated Carousell-Staging'):
    app = Flask(__name__)
    # PUBLIC_URL = 'https://262e7dc94ddb.ngrok.io/'

    @app.route('/start')
    def _start():
        while True:
            try:
                print('Starting app...')
                success, cmd = start(wb_name) 
                if success:
                    print('--Success--')
                    return '--Success--', 200
                else:
                    if cmd == 'Stop':    # Stop Code
                        print('Program Stopped...')
                        return '--Program Stopped--', 400
                    elif cmd == 'Wait':    # Wait 1 min
                        print('Awaiting Query...')
                        time.sleep(60)
                    elif cmd == 'Off':
                        print(
                            f'Sleeping since {datetime.strftime(datetime.now(tz=pytz.timezone("Singapore")),  "%Y-%m-%d %I:%M %p")}')
                        time.sleep(10*60)
                    else:    # Update Failed -> Stop with msg OR Retry in 1 min
                        print('--Program Failed--')
                        return '--Program Failed--', 401
            except Exception as e:
                print(f'--Program Exited Early--\n{e}')
                return '!', 401

    @app.route('/stop')
    def _stop():
        shutdown_hook = request.environ.get('werkzeug.server.shutdown')
        try:
            shutdown_hook()
            print('--End--')
            return '--End--', 0
        except:
            pass

    return app
    # app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5000)))