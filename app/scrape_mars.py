#  Scrapping Mars Web Pages
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt

from splinter import browser

def scrape_all_content():
    # Initialize browser
    browser = Browser("chrome", executable_path="static/chromedriver.exe", headless=True)

    news_title, news_para = mars_news(browser)

    # Run all scraping functions and store results in dictionary called mars_data
    # add datetime now to create a reference to when the scrape took place
    mars_data = {
        "news_title": news_title,
        "news_paragraph": news_para,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemispheres(browser),
        "last_modified": dt.datetime.now()     
    }

    # Stop webdriver and return mars_data
    browser.quit()
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

        # Use parent element to find the first anchor tag <a> and save it as news_title
        news_title = slide_element.find('div', class_='content_title').get_text()

        # Use parent element to find the first news paragraph were the div tag class is 'article_teaser_body'
        # save as a varaiable called 'news_para'

        news_para = slide_element.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_para

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

    except AttributeError:
        return None

    # Combine the base url with the relative path image url to get the entire url for the featured image
    img_url = f'https://www.jpl.nasa.gov{img_url_relative}'

    return img_url

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
    return mars_facts_df.to_html(classes="table table-striped")

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

    except AttributeError:
        # Return None for image error
        title_elem = None
        sample_elem = None
    
    hemispheres = {
        "title": title_elem,
        "img_url": sample_elem
    }

    return hemispheres


if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all_content())

