# scraping app from work done in juypter notebook
# Notes follow:
"""
The scraping app has six functions with the following purpose:

 - mars_news(browser): scrapes https://mars.nasa.gov/news/ the most current news title and news paragraph 
 using splinter Browswer and BeautifulSoup. These are saved as variables
    news_title
    news_para

 - featured_image(browser): scrapes https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars 
 for source (relative) url the featured image and combines that relative url with the base url to
 get the entire url for the featured image. This is then saved as the variable
    img_url

- mars_facts(): scrapes a table from http://space-facts.com/mars/ using the Pandas read_html method. 
The html code to create the table is then returned as output to pass to the MongoDB collection.

- scrape_hemisphere(html_text) and hemispheres(browser) work together to scrape the USGS site at 
https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars to scrape for the hemisphere title and image
which are assigned to variables called 
    title
    img_url

- scrape_all_content() then packages the data collected from the other functions and returns that as a dictionary
"""

#  Scrapping Mars Web Pages
from splinter import Browser 
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt
import re

def scrape_all_content():
    # Initialize browser
    browser = Browser("chrome", executable_path="static/chromedriver.exe", headless=False)

    # identify functions that return more than one variable - mars_news(browser) and featured_image(browser)
    news_title, news_para, news_img_src = mars_news(browser)

    img_url, feature_img_title = featured_image(browser)

    # Run all scraping functions and store results in dictionary called mars_data
    # add datetime now to create a reference to when the scrape took place
    mars_data = {
        "news_title": news_title,
        "news_paragraph": news_para,
        "news_image_src": news_img_src,
        "featured_image": img_url,
        "featured_image_title": feature_img_title,
        "facts": mars_facts(),
        "hemispheres": hemispheres(browser),
        "last_modified": dt.datetime.now()     
    }

    # Stop webdriver and return mars_data
    browser.quit()
    # return the mars_data (dictionary)
    return mars_data



def mars_news(browser):
    # Scrape for Mars News from the NASA News Site at https://mars.nasa.gov/news/
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('ul.item_list li.slide', wait_time=1)

    #Convert the browser html to s BeautifulSoup object
    html = browser.html
    mars_news_soup = BeautifulSoup(html, 'html.parser')

    # include a try and except to handel possible error(s)
    # including a wait time to avoid server busy error message
    try:
        slide_element = mars_news_soup.select_one('ul.item_list li.slide')
        content_title = slide_element.find('div', class_='content_title')

        # Use content_title to get news_title
        news_title = content_title.get_text()

        # Create element img_desc_container to identify container with news paragraph and image.
        # save as a varaiable called 'news_para'
        img_desc_container = slide_element.find('div', class_='image_and_description_container')
        news_para = img_desc_container.get_text()

        # use the parent element to find the image for the news story
        news_img = img_desc_container.find('div', class_='list_image')
        news_img_src_relative = news_img.find('img', class_='').get('src')

        # Create the new_image_url by concatenating the url with the news_img_url_relative
        # Create the new_image_url by concatenating the url with the news_img_url_relative
        news_img_src = f"https://mars.nasa.gov/{news_img_src_relative}"        

    except AttributeError:
        return None, None, None

    return news_title, news_para, news_img_src

def featured_image(browser):
    # Scrape for featured image from JPL at https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Click the full image button
    full_image_element = browser.find_by_id('full_image')[0]
    full_image_element.click()

    # Click the more info button
    # incorporate a delay using browser is_element_present_by_text wait_time augument
    browser.is_element_present_by_text('more info', wait_time=1)

    # since we are looking for a link associated with a button use browser.links and find_by_partial_text
    # reference documentation at https://splinter.readthedocs.io/en/latest/finding.html
    more_info_element = browser.links.find_by_partial_text('more info')
    more_info_element.click()

    # Assign to a BeautifulSoup object and parse using html.parser
    html = browser.html
    img_soup = BeautifulSoup(html, 'html.parser')

    # Use try and accept to handle possible errors
    try:
        # find the relative path image url
        img_url_relative = img_soup.select_one('figure.lede a img').get('src')

        # find the title of the featured image
        feature_title = img_soup.select_one('h1.article_title').string        
        # remove all newlines (n), returnns (r), and tabs (t) form the feature_title (string)
        # using regex .sub method to substitue blank spaces for n, r and t's
        feature_img_title  = re.sub(r"[\n\t\r]*", "", feature_title)

        # use the python .strip method to remove leading and trailing spaces from the feature_img_title
        feature_img_title = feature_img_title.strip()
        

    except AttributeError:
        return None, None

    # Combine the base url with the relative path image url to get the entire url for the featured image
    img_url = f'https://www.jpl.nasa.gov{img_url_relative}'

    return img_url, feature_img_title

def mars_facts():
    # Use try and accept to handle possible errors
    try:
        # use Pandas method read_html to scrape the facts table from http://space-facts.com/mars/ into a DataFrame
        # use method set_index to set index to first column 'Description'
        # use inplace augument = True to change DataFrame inplace

        mars_facts_df = pd.read_html('http://space-facts.com/mars/')[0]        

    except BaseException:
        return None    

    mars_facts_df.columns=['Description', 'Mars']
    mars_facts_df.set_index('Description', inplace=True)

    # use method to_html to convert DataFrame to HTML and add bootstrap table templating
    return mars_facts_df.to_html(classes="table table-sm table-bordered table-hover table-dark m-1 p-1")

def hemispheres(browser):
    # scrape the USGS site at https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars
    # for images of Mar's hemispheres
    # use technique to break up long url
    url = (
        "https://astrogeology.usgs.gov/search/"
        "results?q=hemisphere+enhanced&k1=target&v1=Mars"
    )

    browser.visit(url)

    #  interate through the four(4) hemispheres by clicking the link to hemisphere 
    hemisphere_image_urls = []

    for i in range(4):
        # Find link to each hemisphere and click through
        browser.find_by_css("a.product-item h3")[i].click()

        # pass the link to the function below to scrape for the url
        hemisphere_data = scrape_hemisphere(browser.html)

        # Append the hemisphere object to the hemisphere_image_urls list
        hemisphere_image_urls.append(hemisphere_data)

        # navigate backwards to get the url for the next hemisphere
        browser.back()

    return hemisphere_image_urls

def scrape_hemisphere(html_text):
    # parse html text and create a Beautifullsoup object
    hemi_soup = BeautifulSoup(html_text, "html.parser")

    # add a try and except to handle potential errors
    try:
        title_elem = hemi_soup.find("h2", class_="title").get_text()
        sample_elem = hemi_soup.find("a", text="Sample").get("href")
        para_elem = hemi_soup.find("p", class_="").get_text()

    except AttributeError:
        # Return None for image error
        title_elem = None
        sample_elem = None
        para_elem = None
    
    hemispheres = {
        "title": title_elem,
        "img_url": sample_elem,
        "paragraph": para_elem
    }

    return hemispheres
    

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all_content())

