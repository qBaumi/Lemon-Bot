from __future__ import print_function

import asyncio
import datetime
import json

from pytz import timezone

from config import emails
from config import guilds
from googleapiclient.discovery import build
import cogs.essentialfunctions as es
from discord.ext import commands, tasks
from google.oauth2 import service_account

with open("./googlesheets/spreatsheetid.txt") as f:
    SPREADSHEET_ID = f.read()
with open("./json/lockedranges.json", "r", encoding="utf-8") as f:
    LockRanges = json.load(f)
# Logging creds idk I copied it
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = './googlesheets/keys.json'
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)

# Call the Sheets API
sheet = service.spreadsheets()

#value = [["hello world!"]]
# SET majorDimension FOR COLUMNS OR ROWS!!!
#result = sheet.values().update(spreadsheetId=SPREADSHEET_ID, valueInputOption="RAW", range="Sheet5!A1", body={"values": value}).execute()



def getColumnNumber(columnName):
    # columnName as A, AA, ABC
    columnLetters = list(columnName)
    print(columnLetters)

    columnValue = 0
    lettersCount = len(columnLetters)
    for i in range(lettersCount):
        columnValue = columnValue + 26 ** (lettersCount - i - 1) * (ord(columnLetters[i]) - 64)

    return columnValue







class googlesheets(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.lock_sheet_timer.start()


    @commands.command()
    @commands.has_any_role("Admins", "HM", "Developer")
    async def lock(self, ctx):
        self.lock_sheet(LockRanges[0])

    @tasks.loop(seconds=59)
    async def lock_sheet_timer(self):
        lockrangelist = LockRanges
        hour = datetime.datetime.now().hour
        min = datetime.datetime.now().minute
        print(min)
        for range in lockrangelist:
            #print(datetime.datetime.now().strftime("%d-%m-%Y"))
            #print(range["date"])
            #print(datetime.datetime.now().strftime("%H:%M"))
            #print(range["time"])
            if datetime.datetime.now().strftime("%d-%m-%Y") == range["date"] and range["time"] == datetime.datetime.now().strftime("%H:%M"):
                self.lock_sheet(range)
                channel = await self.client.fetch_channel(963720915575779358)
                await channel.send("Sheet was succesfully locked!")
                await asyncio.sleep(1)

    def lock_sheet(self, range):
        Editors = {
            "users": emails,
            "groups": [],
            "domainUsersCanEdit": False
        }

        GridRange = {
            "sheetId": range["sheetId"],
            "startRowIndex": range["range"]["startRow"],
            "endRowIndex": range["range"]["endRow"],
            "startColumnIndex": getColumnNumber(range["range"]["startCol"]),
            "endColumnIndex": getColumnNumber("EZ")
        }

        ProtectedRange = {
            "range":
                GridRange
            ,
            "description": f"{range['date']} - LOCKED",  # title of the locked thingy
            "warningOnly": False,
            "requestingUserCanEdit": False,
            "unprotectedRanges": [],
            "editors":
                Editors

        }


        requests = []
        requests.append({
            "addProtectedRange": {
                "protectedRange": ProtectedRange
            }
        })

        body = {
            'requests': requests
        }
        print(body)
        response = service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body=body).execute()
        print(response)

async def setup(client):
    await client.add_cog(googlesheets(client), guilds=guilds)
