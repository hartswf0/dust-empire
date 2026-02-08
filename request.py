#
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Example URL (replace with the specific Addis property site)
url = 'https://www.mekina.net/'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

properties = []

# This part depends on the website's specific HTML structure
for item in soup.find_all('div', class_='listing-item'):
    price = item.find('span', class_='price').text.strip()
    location = item.find('div', class_='location').text.strip()
    properties.append({'Price': price, 'Location': location})

df = pd.DataFrame(properties)
print(df.head())