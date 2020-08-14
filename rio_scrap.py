import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
#
classes = {'classcolor1': 'Warrior', 'classcolor2': 'Paladin', 'classcolor8': 'Mage', 
           'classcolor4': 'Rogue',  'classcolor5': 'Priest',  'classcolor10': 'Monk',  
           'classcolor12': 'Demon Hunter', 'classcolor11': 'Druid', 'classcolor6': 'Death Knight', 
           'classcolor3': 'Hunter', 'classcolor9': 'Warlock', 'classcolor7': 'Shaman'}
#
affixes = {'affix10': 'Fortified', 'affix11': 'Bursting', 
           'affix3': 'Volcanic', 'affix120': 'Awakened',
           'affix7': 'Bolstering', 'affix2': 'Skittish', 
           'affix8': 'Sanguine', 'affix14': 'Quaking', 
           'affix12': 'Grevious', 'affix9': 'Tyrannical',
           'affix5': 'Teeming', 'affix13': 'Explosive',
           'affix4': 'Necrotic' }
#
num = 0
URL = 'https://raider.io/mythic-plus-rankings/season-bfa-4/all/world/leaderboards/%s#content'
df = None
#
for num in range(5):
    print('Fetching Page... ' + (URL % num))
    page = requests.get(URL % num)    
    soup = BeautifulSoup(page.text, 'html.parser')
    table = soup.find('table', {'class': 'slds-table slds-table--bordered slds-table--striped rio-rankings-table'})
    
    
    # Change Class Names
    for i in table.find_all('i', {'class': 'rio-spaced-element--small fa fa-star text-gold'}):
        i.string = ' x'
    
    
    # Fix Affixes String
    for a in table.find_all('a', {'class': 'rio-spaced-element--small'}):    
        for div in a.find_all('div'):
            div.string = affixes[re.sub('[\"\=\[\]\']', '', str(a.get('rel')))] + ' - '
    
    # Change Class Names
    for a in table.find_all('a', {'class': re.compile('class-color')}):  
        a.string = classes[re.sub('[\"\=\[\]\-\']', '', str(a.get('class')))] + ' - '

    # Get Faction Info
    for div in table.find_all('div', {'class': re.compile('icon-faction')}):
        div.string = div.get('class')[1].split('-')[-1]

    # Reads the object and set the DataFrame        
    df_list = pd.read_html(str(table), flavor='bs4')

    if(df is None):
        df = df_list[0]
    else:
        df = pd.concat([df, df_list[0]], ignore_index=True)        
#
# Data clean up
df['Affixes'] = df['Affixes'].astype(str).str[:-1]
df['Tank'] = df['Tank'].astype(str).str[:-1]
df['Healer'] = df['Healer'].astype(str).str[:-1]
df['DPS'] = df['DPS'].astype(str).str[:-1]
df = df.rename(columns={'Unnamed: 9':'Faction'})
#
# Fix Column for keystone upgraded
df['Upgraded'] = df['Level'].str.split(' ', n = 1, expand = True)[1]
df['Level'] = df['Level'].str.split(' ', n = 1, expand = True)[0]
df = df[['Rank', 'Dungeon', 'Level', 'Upgraded', 'Time', 'Affixes', 'Tank', 'Healer', 'DPS', 'Score', 'Faction']]
df['Upgraded'].replace(re.compile('x'), 1, inplace=True)
df['Upgraded'].fillna(0, inplace=True)
#
# Save CSV File
df.to_csv(r'rio_scraped_data.csv')
