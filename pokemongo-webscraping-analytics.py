#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from bs4 import BeautifulSoup
import pandas as pd
from pandas.plotting import scatter_matrix
import matplotlib.pyplot as plt
import numpy as np

rootdir = '2017W2'

#ALL FILES
d = dict()
process_count = 0

for subdir, dirs, files in os.walk(rootdir): #source: https://stackoverflow.com/questions/19587118/iterating-through-directories-with-python
    lst = [subdir, dirs, files] #line18-25 is necessary for me to go around a .DS_store file I have. If you don't have it, feel free to remove.
    if lst[0] != '2017W2':
        subdir = lst[0]
        dirs = lst[1]
        files = lst[2]
        for file in files:
            if file == '.DS_Store':
                continue
                
            dt = int(subdir[7:11]), int(subdir[13:14]), int(subdir[15:]), int(file[:2]), int(file[3:5])
            #print(dt)
            
            android_avg_rating = []
            android_total_ratings = []
            android_file_size = []
            
            android_rating_5 = []
            android_rating_4 = []
            android_rating_3 = []
            android_rating_2 = []
            android_rating_1 = []
            
            ios_current_ratings = []
            ios_all_ratings = []
            ios_file_size = []
    
            if 'android' in file:
                
                #OPEN FILE
                fpath = os.path.join(subdir,file)
                with open(fpath, 'r') as f:
                    data = f.read()
                and_soup = BeautifulSoup(data, 'lxml')
                
                #GET AVERAGE SCORE
                tag = and_soup.find(attrs={'itemprop':'ratingValue'}) #help: https://stackoverflow.com/questions/16687493/access-the-content-attribute-of-the-description-meta-tag
                avg_scr = tag['content']
                #avg_scr = and_soup.find('div', {'class': 'score'}).get_text().strip()
                
                #GET NUMBER OF REVIEWS
                rev_num = and_soup.find('span', {'class': 'reviews-num'}).get_text().strip().replace(',','')
                
                #GET FILE SIZE
                file_size_and = ''
                
                try:
                    file_size = and_soup.find('div', itemprop ='fileSize').get_text().strip()
                    for char in file_size:
                        if char.isdigit() == True:
                            file_size_and += char
                except:
                    continue
                
                #GET STAR RATINGS
                
                ratings_5 = and_soup.find('div', {'class': 'rating-bar-container five'}).get_text().strip().replace(',','')[4:]
                ratings_4 = and_soup.find('div', {'class': 'rating-bar-container four'}).get_text().strip().replace(',','')[4:]
                ratings_3 = and_soup.find('div', {'class': 'rating-bar-container three'}).get_text().strip().replace(',','')[4:]
                ratings_2 = and_soup.find('div', {'class': 'rating-bar-container two'}).get_text().strip().replace(',','')[4:]
                ratings_1 = and_soup.find('div', {'class': 'rating-bar-container one'}).get_text().strip().replace(',','')[4:]
                
                #ADD TO LIST
                android_avg_rating.append(avg_scr)
                android_total_ratings.append(rev_num)
                android_file_size.append(file_size_and)
                
                android_rating_5.append(ratings_5)
                android_rating_4.append(ratings_4)
                android_rating_3.append(ratings_3)
                android_rating_2.append(ratings_2)
                android_rating_1.append(ratings_1)
                
                try:
                    android_data = {'android_avg_rating': float(android_avg_rating[0]), 
                                    'android_total_ratings': int(android_total_ratings[0]), 
                                    'android_rating_1': int(android_rating_1[0]), 
                                    'android_rating_2': int(android_rating_2[0]), 
                                    'android_rating_3': int(android_rating_3[0]), 
                                    'android_rating_4': int(android_rating_4[0]), 
                                    'android_rating_5': int(android_rating_5[0]), 
                                    'android_file_size': int(android_file_size[0])}
#                     if dt in d:
#                         d[dt].update(android_data)
#                     else:
                    d[dt] = android_data 
                except:
                    continue

            elif 'ios' in file:
                fpath = os.path.join(subdir, file)
                with open(fpath, 'r') as f:
                    data = f.read()
                ios_soup = BeautifulSoup(data, 'lxml')
                
                #COMBINED RATINGS
                curr_rating = ''
                rating = ios_soup.find('span', {'class':'rating-count'}).get_text().strip()
                for char in rating:
                    if char.isdigit() == True:
                        curr_rating += char
                        
                #ALL RATINGS
                all_ratings = ''
                ALL_ratings = ios_soup.find('span', class_='rating-count', itemprop = False).get_text().strip()
                for char in ALL_ratings:
                    if char.isdigit() == True:
                        all_ratings += char
                
                #FILE SIZE
                file_size_ios = ''
                file_size_lst = ios_soup.findAll('li')
                
                
                for fs in file_size_lst:
                    try:
                        temp = fs.get_text()
                        if 'Size:' in temp:
                            for char in temp:
                                if char.isdigit() == True:
                                    file_size_ios += char
                    except:
                        continue
                
                #ADD TO LIST
                ios_current_ratings.append(curr_rating)
                ios_all_ratings.append(all_ratings)
                ios_file_size.append(file_size_ios)
                
                ios_data = {'ios_current_ratings': int(ios_current_ratings[0]), 
                             'ios_all_ratings': int(ios_all_ratings[0]), 
                             'ios_file_size': int(ios_file_size[0])}
                
                if dt in d:
                    d[dt].update(ios_data)
                else:
                    continue
                    
            process_count +=1
            tot_files = len(next(os.walk(rootdir))[1])*len(files) #help: https://stackoverflow.com/questions/29769181/count-the-number-of-folders-in-a-directory-and-subdirectories
            percentage = process_count/tot_files*100
            print('Computing {} {}... percentage complete {}%'.format(subdir,file,str(percentage)))
                    
#Convert into pandas dataframe
df = pd.DataFrame(d)
df = df.transpose()

#save files
df.to_json('data.json')
df.to_excel('data.xlsx')
df.to_csv('data.csv')

#3.3 Data Exploration
#find the count/mean/std/min/25%/50%75%/max values for each 11 variables.
df.describe()

#Use scatter_matrix() method to find pairs of variables with high correlations (either positive or negative).
scatter_matrix(df, figsize=(20,20))
plt.show()

#For identified pairs (around 5), calculate the Pearon’s correlation coefficients. You can use corrcoef() function in numpy module for this.
corr_1 = np.corrcoef(df['ios_all_ratings'], df['ios_current_ratings'])
corr_2 = np.corrcoef(df['android_total_ratings'], df['android_rating_1'])
corr_3 = np.corrcoef(df['android_total_ratings'], df['android_rating_5'])
corr_4 = np.corrcoef(df['ios_all_ratings'], df['android_total_ratings'])
corr_5 = np.corrcoef(df['ios_file_size'], df['android_file_size'])

#Use matplotlib or other tools to create time series graphs for each of the 11 variables.
fig = plt.figure(figsize=(15,15)) #source: https://stackoverflow.com/questions/14632729/matplotlib-make-x-axis-longer
ax = df['ios_all_ratings'].plot()
ax.set_xlabel('dates')
ax.set_ylabel('# of iOS ratings')
plt.show()

fig = plt.figure(figsize=(15,15))
ax = df['ios_current_ratings'].plot()
ax.set_xlabel('dates')
ax.set_ylabel('# of ios ratings')
plt.show()

fig = plt.figure(figsize=(15,15))
ax = df['ios_file_size'].plot()
ax.set_xlabel('dates')
ax.set_ylabel('file size (MB)')
plt.show()

fig = plt.figure(figsize=(15,15))
ax = df['android_rating_5'].plot()
ax.set_xlabel('dates')
ax.set_ylabel('# of android ratings')
plt.show()

fig = plt.figure(figsize=(15,15))
ax = df['android_rating_4'].plot()
ax.set_xlabel('dates')
ax.set_ylabel('# of android ratings')
plt.show()

fig = plt.figure(figsize=(15,15))
ax = df['android_rating_3'].plot()
ax.set_xlabel('dates')
ax.set_ylabel('# of android ratings')
plt.show()

fig = plt.figure(figsize=(15,15))
ax = df['android_rating_2'].plot()
ax.set_xlabel('dates')
ax.set_ylabel('# of android ratings')
plt.show()

fig = plt.figure(figsize=(15,15))
ax = df['android_rating_1'].plot()
ax.set_xlabel('dates')
ax.set_ylabel('# of android ratings')
plt.show()

fig = plt.figure(figsize=(15,15))
ax = df['android_total_ratings'].plot()
ax.set_xlabel('dates')
ax.set_ylabel('# of android ratings')
plt.show()

fig = plt.figure(figsize=(15,15))
ax = df['android_avg_rating'].plot()
ax.set_xlabel('dates')
ax.set_ylabel('# of android ratings')
plt.show()

fig = plt.figure(figsize=(15,15))
ax = df['android_file_size'].plot()
ax.set_xlabel('dates')
ax.set_ylabel('file size (MB)')
plt.show()