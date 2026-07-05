import os
import json
import datetime
import requests
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

def update_nse_bhavcopy():
    try:
        # 1. तारीख सेट करना (आज की भावकॉपी के लिए)
        # अगर शनिवार/रविवार है तो यह पिछले कार्यदिवस का डेटा उठाएगा
        today = datetime.datetime.now()
        if today.weekday() == 5: # Saturday
            today = today - datetime.timedelta(days=1)
        elif today.weekday() == 6: # Sunday
            today = today - datetime.timedelta(days=2)
            
        date_str = today.strftime("%d%m%Y") # Format: DDMMYYYY
        
        # NSE भावकॉपी का आधिकारिक आर्काइव URL
        url = f"https://archives.nseindia.com/products/content/sec_bhavdata_full_{date_str}.csv"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        
        print(f"Fetching data for date: {date_str}...")
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print("NSE Bhavcopy is not uploaded yet or today is a market holiday.")
            return

        # CSV डेटा को पढ़ना
        with open("bhavcopy.csv", "w") as f:
            f.write(response.text)
            
        df = pd.read_csv("bhavcopy.csv")
        
        # कॉलम के आसपास के फालतू स्पेस को हटाना
        df.columns = df.columns.str.strip()
        df['SERIES'] = df['SERIES'].str.strip()
        df['SYMBOL'] = df['SYMBOL'].str.strip()
        
        # केवल 'EQ' (Equity) सीरीज के शेयर फिल्टर करना
        df = df[df['SERIES'] == 'EQ']
        
        # हमारे काम के कॉलम: Symbol, Close Price, Delivery Percentage
        final_df = df[['SYMBOL', 'CLOSE_PRICE', 'DELIV_PER']]
        
        # गिटहब सीक्रेट्स से गूगल क्रेडेंशियल्स लोड करना
        creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_info(creds_json, scopes=scopes)
        client = gspread.authorize(creds)
        
        # गूगल शीट को उसकी ID से खोलना
        sheet_id = os.environ["SPREADSHEET_ID"]
        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.sheet1 # पहली शीट (Sheet1)
        
        # शीट को साफ करके नया डेटा लिखना
        worksheet.clear()
        
        # हेडर और डेटा को लिस्ट फॉर्मेट में बदलना
        data_to_write = [final_df.columns.values.tolist()] + final_df.values.tolist()
        
        # शीट में अपडेट करना
        worksheet.update('A1', data_to_write)
        print("Google Sheet updated successfully with delivery percentage!")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    update_nse_bhavcopy()
