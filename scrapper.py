# We want to make an scrapper for indeed.co.uk, where the job title and location can be personalised
#Inspired in article https://medium.com/@msalmon00/web-scraping-job-postings-from-indeed-96bd588dcb4b

import requests

try:
    from bs4 import BeautifulSoup
except :
    from BeautifulSoup import BeautifulSoup 
import pandas as pd
import time
import streamlit as st
from geopy import Nominatim

import numpy as np


def scrapper(title, location = "United Kingdom"):

    #Add job title to search. Any space will be reeplaced with a + symbol 

    title = title
    title = title.replace(" ", "+")

    #Add location to search. Any space will be reeplaced with a + symbol. No case sensitive
    location =location
    location = location.replace(" ", "+")

    base_url = "https://www.indeed.co.uk/jobs?q="+title+"&l="+location


    #First url to check for number of ads stracting
    first_url = base_url+"&start=0"

    #conducting a request of the stated URL above:
    first_page = requests.get(base_url)

    #specifying a desired format of “page” using the html parser - this allows python to read the various components of the page, rather than treating it as one long string.
    soup = BeautifulSoup(first_page.text, "html.parser")

    #Extract all the posts of the page
    posts =soup.find_all(name="div", attrs={"class":"row"})

    def extract_n_ads(soup):
        #Extract the total number of add in the search
        n_ads_soup = soup.find("div", {"id":"searchCountPages"}) 
        try:
            n_ads = int(str(n_ads_soup)[str(n_ads_soup).find("of")+2:str(n_ads_soup).find("jobs")])
        except:
            st.write("Error!")
        return n_ads



    #Extract all the posts of the page
    posts =soup.find_all(name="div", attrs={"class":"row"})

    def element_extraction(post_list):
        posts = post_list
        #Extract all the data from the post lists
        ads = []
        for i in range(len(list(posts))):
            
            ad = []
            title = posts[i].find_all(name="a", attrs={"data-tn-element":"jobTitle"})[0].string
            ad.append(title)
            
            company = posts[i].find_all(name="span", attrs={"class":"company"})[0].text.strip()
            ad.append(company)
            
            try:
                rating = float(posts[i].find_all(name="span", attrs={"class":"ratingsDisplay"})[0].text.strip())
            except:
                rating = "NaN" 
                
            ad.append(rating)
            

            try:
                location = posts[i].find_all(name="span", attrs={"class":"location accessible-contrast-color-location"})[0].text.strip()
            except:
                location = "NaN"
                
            
            ad.append(location)
            

            if "Remote" in str(posts[i]):
                remote = "Remote"
            elif "remote" in str(posts[i]):
                remote = "Temporarily remote"
            else:
                remote = "No"
            
            ad.append(remote)
            

            ad_url =posts[i].find_all(name="a", attrs={"data-tn-element":"jobTitle"})[0].get('href')
            url = "https://www.indeed.co.uk" + str(ad_url)
            ad.append(url)

            ads.append(ad)

        return ads

    search_index = 0
    all_adverts = []
    n_ads = extract_n_ads(soup)

    while search_index < n_ads:
        print(search_index)
        #Creating an url with the search index
        url = base_url+"&start="+str(search_index)
        #conducting a request of the stated URL above:
        page = requests.get(url)

        #specifying a desired format of “page” using the html parser - this allows python to read the various components of the page, rather than treating it as one long string.
        soup = BeautifulSoup(page.text, "html.parser")   
        
        #Extract all the posts of the page
        posts =soup.find_all(name="div", attrs={"class":"row"})

        all_adverts = all_adverts + (element_extraction(posts))

        search_index = search_index + 15
        
        print(len(all_adverts))
        time.sleep(1)

    return all_adverts


st.title("Welcome to the indeed.co.uk crapper")
if st.button("See Readme"):
    st.write("""This is an scrapper for Indeed.co.uk, the job ads website. This project has three parts, an advance webscrapper, a little exploratory analysis of those ads and a 
    visualization tool using streamlite. Although sleepers where added in order to avoid IP ban by the website, some times the connection was blocked. 
    I recomend use an VPN anc change server, or a similar solution, if it's going to be tried more than once in a short time period.
    The city name to coordinates translation is really slow too, making that the map take ages in appear, depending of the number of ads. Code in https://github.com/jfpalomeque/indeed_scrapper""")

st.write("## Write here the job title to search in Indeed.co.uk")
title_input = st.text_input("Job title", "Data Science")

if st.button("Run!"):



    test = scrapper(title_input)

    df = pd.DataFrame(test)
    df.drop_duplicates()
    df.columns = ["job_Title", "company", "rating", "location", "remote","ad_url"]
    
    n_ads_found = len(df)-1
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    avg_rate = df["rating"].mean()
    location_freq = df.location.value_counts()
    

    st.write("The total number of ads scrapped for " + title_input + " jobs is " + str(n_ads_found))
    st.write("The average rating over 5 of ads scrapped for " + title_input + " jobs is " + str(avg_rate))
    st.write("The locations of ads scrapped for " + title_input + " jobs are ")
    st.write(location_freq)


    st.write("Ads DataFrame")
    st.write(df)



    st.write("Map / Please wait, coords process can take a while!!")    
    geolocator = Nominatim(user_agent="indeed_scrapper")

    location_coords = []
    for line in df.location:
        loc_row = []
        location = geolocator.geocode(line)
        loc_row.append(line)
        loc_row.append(location.latitude)
        loc_row.append(location.longitude)
        location_coords.append(loc_row)
        print (location.latitude, location.longitude)
        time.sleep(1)

    location_coords = pd.DataFrame(location_coords)
    location_coords.columns = ["location", "latitude", "longitude"]
    st.map(location_coords)

    
    

