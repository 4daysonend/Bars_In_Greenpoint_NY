import os
import requests
import gspread
from dotenv import load_dotenv
from pprint import pprint
import time

# Load environment variables from a .env file
load_dotenv()

# Google API configuration
API_KEY = os.getenv('GOOGLE_API_KEY')  # Ensure your .env file contains GOOGLE_API_KEY=your_api_key
url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'

# Parameters for the GET request
params = {
    'location': '40.7305,-73.9515',  # coordinates (Williamsburg, NY)
    'radius': 1000,  # 1000 meters radius
    'type': 'bar',  # Searching for bars
    'key': API_KEY
}

# Function to fetch places with pagination
def fetch_places(params):
    all_bars = []  # To store all fetched bars
    while True:
        # Make the GET request to the Google Places API
        response = requests.get(url, params=params)
        if response.status_code == 200:
            # Parse the response
            places = response.json().get('results', [])
            for place in places:
                name = place.get('name', 'No name available')
                address = place.get('vicinity', 'No address available')
                rating = place.get('rating', 'No rating')
                review_count = place.get('user_ratings_total', 0)

                # Fetch service options or note 'No service options'
                service_options = place.get('types', [])
                if service_options:
                    service_options_str = ', '.join(service_options)
                else:
                    service_options_str = 'No service options'

                # Store the bar details
                all_bars.append({
                    'name': name,
                    'address': address,
                    'rating': rating,
                    'review_count': review_count,
                    'service_options': service_options_str
                })
            
            # Output the information to console
            for bar in all_bars:
                print(f"Name: {bar['name']}")
                print(f"Address: {bar['address']}")
                print(f"Rating: {bar['rating']}")
                print(f"Number of Reviews: {bar['review_count']}")
                print(f"Service Options: {bar['service_options']}\n")
            
            # Check if there's a next page token for more results
            next_page_token = response.json().get('next_page_token')
            if next_page_token:
                # Update params with next page token
                params['pagetoken'] = next_page_token
                # Google recommends a short delay before the next request
                time.sleep(2)
            else:
                # No more results, break out of the loop
                break
        else:
            print(f"Error: {response.status_code}")
            pprint(response.json())
            break
    
    return all_bars

# Fetch the bar data
bars = fetch_places(params)

# Connecting to Google Sheets and outputting the data
def output_to_sheet(bars):
    gc = gspread.service_account(filename='creds.json')
    sh = gc.open('Barstovisit').sheet1
    
    # Append rows to the Google Sheet
    for bar in bars:
        sh.append_row([bar['name'], bar['address'], str(bar['rating']), str(bar['review_count']), bar['service_options']])

# Output the bar data to Google Sheets
if bars:
    output_to_sheet(bars)
else:
    print("No bars found to add to the Google Sheet.")
