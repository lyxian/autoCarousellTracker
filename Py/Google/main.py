### GOOGLE SHEETS API ###
from oauth2client.service_account import ServiceAccountCredentials
from cryptography.fernet import Fernet
import gspread
import json
import os

def getCredentials():
    key = bytes(os.getenv('KEY'), 'utf-8')
    encrypted = bytes(os.getenv('CLIENT_SECRET'), 'utf-8')
    return json.loads(Fernet(key).decrypt(encrypted))

def spreadSheetClient():
    scope = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        getCredentials(), scope)
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

if __name__ == '__main__':
    pass
