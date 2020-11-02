# Flask Server to serve up index.html file in the templates folder
from flask import Flask, render_template
from flask_pymongo import PyMongo
import scrape_mars

app = Flask(__name__)

# start MongoDB Compass and estalbish a connection
# setup a MongoDB connection using flask_pymongo
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)

# create a home ("/") route
@app.route("/")
def index():
    # identify the name of the database collection ("mars")
    mars = mongo.db.mars.find_one()
    # use the render_template
    return render_template("index.html", mars=mars)

@app.route("/scrape")
def scrape():
    # create mars collection in MongoDB mars database
    mars = mongo.db.mars

    # call the function scrape_all_content and assign to variable mars_data (used in scrape app)
    mars_data = scrape_mars.scrape_all_content()
    mars.update({}, mars_data, upsert=True)
     
    return "Scraping Complete - Return homepage and refresh to view scaped Mars news, facts and images"
    
if __name__ == "__main__":
    app.run()