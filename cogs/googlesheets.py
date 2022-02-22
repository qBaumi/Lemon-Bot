from __future__ import print_function

with open("./googlesheets/spreatsheetid.txt") as f:
    SPREADSHEET_ID = f.read()
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import cogs.essentialfunctions as es
from discord.ext import commands
import discord, asyncio
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = './googlesheets/keys.json'

creds = None
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# The ID and range of a spreadsheet.



service = build('sheets', 'v4', credentials=creds)

# Call the Sheets API
sheet = service.spreadsheets()


#value=[["hello world!"]]
# SET majorDimension FOR COLUMNS OR ROWS!!!
#result = sheet.values().update(spreadsheetId=SPREADSHEET_ID, valueInputOption="RAW", range="test!A1", body={"values":value}, insertDataOption="INSERT_COLUMNS").execute()
#values = result.get('values', [])
#print(result)

class googlesheets(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_any_role("Admins", "HM", "Developer")
    async def initsheet(self, ctx):
        mysql = f'SELECT id, safe FROM users'
        es.mycursor.execute(mysql)
        data = es.mycursor.fetchall()
        print(data)
        useridcol = []
        balcol = []
        """
        for user in data:
            if user[1] != 0:
                userid = user[0]
                #bal = user[1]
                name = await self.client.fetch_user(userid)
                useridcol.append([str(name)])
                balcol.append([user[1]])

        useridres = sheet.values().update(spreadsheetId=SPREADSHEET_ID, valueInputOption="RAW", range="test!A2", body={"values":useridcol}).execute()
        balres = sheet.values().update(spreadsheetId=SPREADSHEET_ID, valueInputOption="RAW", range="test!B2", body={"values":balcol}).execute()
        #print(useridres)
        print(balres)
        """

    @commands.command()
    @commands.has_any_role("Admins", "HM", "Developer")
    async def lock(self, ctx):
        print(sheet.get(spreadsheetId=SPREADSHEET_ID))

        requests = []
        # Change the spreadsheet's title.
        title = "LCS Spring Split 2022"


        requests.append({
            'updateSpreadsheetProperties': {
                'properties': {
                    'title': title
                },
                'fields': 'title'
            }
        })
        # Find and replace text
        requests.append({
            'findReplace': {
                'find': find,
                'replacement': replacement,
                'allSheets': True
            }
        })
        # Add additional requests (operations) ...

        body = {
            'requests': requests
        }
        response = service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body=body).execute()
        find_replace_response = response.get('replies')[1].get('findReplace')
        print('{0} replacements made.'.format(
            find_replace_response.get('occurrencesChanged')))



def setup(client):
    client.add_cog(googlesheets(client))