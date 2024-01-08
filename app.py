from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import csv

app = Flask(__name__)

@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review', methods=['POST', 'GET'])  # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ", "")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']

            reviews = []

            for page in range(1, 20):  # Scraping reviews from the first 5 pages (you can adjust the range accordingly)
                page_url = f"{productLink}&page={page}"
                prodRes = requests.get(page_url)
                prodRes.encoding = 'utf-8'
                prod_html = bs(prodRes.text, "html.parser")
                commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})

                for commentbox in commentboxes:
                    try:
                        name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                    except:
                        name = 'No Name'

                    try:
                        rating = commentbox.div.div.div.div.text
                    except:
                        rating = 'No Rating'

                    try:
                        commentHead = commentbox.div.div.div.p.text
                    except:
                        commentHead = 'No Comment Heading'

                    try:
                        comtag = commentbox.div.div.find_all('div', {'class': ''})
                        custComment = comtag[0].div.text
                    except Exception as e:
                        print("Exception while creating dictionary: ", e)

                    mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                              "Comment": custComment}
                    reviews.append(mydict)

            # Writing to CSV file
            filename = f"{searchString}_reviews.csv"
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ["Product", "Name", "Rating", "CommentHead", "Comment"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for review in reviews:
                    writer.writerow(review)

            return render_template('results.html', reviews=reviews)
        except Exception as e:
            print('The Exception message is: ', e)
            return 'something is wrong'
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8001, debug=True)
