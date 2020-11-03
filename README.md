# TA_Demo_Web_Scraping_II

This webscraping demo uses the following elements:

* a Juypter notebook to explore the code necessary to scrape four Mars related websites using Beautifulsoup

* an HTML file (index.html) to display the scraped information. This file uses Bootstrap (a front-end open source toolkit). The HTML file contains placeholders ({{ }}) to connect data from a MongoDB database to the webpage. The HTML includes a button what when selected will scrape each of the four websites

* The webpage is "served-up" using a flask application (app.py) that contains two routes: a "home" route ("/"), and a "scrape" route (/scrape). 

* a Scraping application (scrape_mars.py) that uses the code developed in the Juypter notebook and scrapes the four websites using splinter's Browser "tool." Within the scraping app, four seperate functions were created, each scraping one of the websites. An additional function (scrape_all_content) is used to pass the scraped informaiton to a MongoDB database. The MongoDB then passes the data within the collection to the served-up html file.
