import gspread

gc = gspread.service_account(filename='creds.json')

sh = gc.open('Barstovisit').sheet1

sh.update
