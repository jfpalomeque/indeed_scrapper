# We want to make an scrapper for indeed.co.uk, where the job title and location can be personalised
#Inspired in article https://medium.com/@msalmon00/web-scraping-job-postings-from-indeed-96bd588dcb4b

import requests
import bs4
from bs4 import BeautifulSoup
import pandas as pd
import time


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
        n_ads = int(str(n_ads_soup)[str(n_ads_soup).find("of")+2:str(n_ads_soup).find("jobs")])
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
                rating = posts[i].find_all(name="span", attrs={"class":"ratingsDisplay"})[0].text.strip()
            except:
                rating = "Nan" 
                
            ad.append(rating)
            

            try:
                location = posts[i].find_all(name="span", attrs={"class":"location accessible-contrast-color-location"})[0].text.strip()
            except:
                location = "Nan"
                
            
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

    return n_ads, all_adverts


test = scrapper("Data Science")

