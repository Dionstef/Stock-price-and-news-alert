import requests
import datetime
import smtplib

# ------------------------------- CONSTANTS -------------------------------#
STOCK = "TSLA"  # Insert the name of the stock that you want to track the price for
API_KEY_STOCK = ""  # Insert your key from the website https://www.alphavantage.co/
STOCK_ENDPOINT = "https://www.alphavantage.co/query"

NEWS = "Tesla Inc"  # Insert the name of the company that you want to get the news for
API_KEY_NEWS = ""  # Insert your key from the website https://newsapi.org/
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

MY_EMAIL = "abc@gmail.com"  # Insert your e-mail address here ex abc@gmail.com
MY_PASS = ""  # Insert your application password of your e-mail
EMAIL_PROVIDER = "smtp.gmail.com"  # Insert your email provider ex smtp.gmail.com

# -------------------------------  STOCK PRICE -------------------------------#
# Get the daily time series of the stock through the API
parameters_stock = {
    "function": "TIME_SERIES_DAILY_ADJUSTED",
    "symbol": STOCK,
    "apikey": API_KEY_STOCK
}
stock_data = requests.get(STOCK_ENDPOINT, params=parameters_stock)
stock_data.raise_for_status()
stock_data = stock_data.json()["Time Series (Daily)"]

# Create a list with the data
price_list = [value for (key, value) in stock_data.items()]

# Find the closing prices for yesterday and the day before yesterday
price_of_yesterday = float(price_list[0]["4. close"])
price_of_the_day_before_yesterday = float(price_list[1]["4. close"])

# Check the difference in price between yesterday and the day before yesterday
percentage_difference = (price_of_yesterday - price_of_the_day_before_yesterday) / price_of_the_day_before_yesterday * 100

# -------------------------------  STOCK NEWS -------------------------------#
# If the price difference is more than 5%
if abs(percentage_difference) >= 5:

    # Get today's articles
    today = datetime.datetime.now()
    day_of_the_article = str(today).split()[0]
    parameters_news = {
        "q": NEWS,
        "from": day_of_the_article,
        "to": day_of_the_article,
        "sortBy": "popularity",
        "apiKey": API_KEY_NEWS
    }

    news_data = requests.get(NEWS_ENDPOINT, params=parameters_news)
    news_data.raise_for_status()

    total_num_articles = news_data.json()['totalResults']

    # Check if there are at least 3 articles
    if total_num_articles >= 3:
        articles_to_get = 3
    else:
        articles_to_get = total_num_articles

    # Create a list with the first 3 articles
    sliced_list = news_data.json()['articles'][slice(articles_to_get)]
    article_formatted = [f"\u2022 Headline: {article['title']}. \n\u2022 Brief:{article['description']} \n\u2022 URL: {article['url']}"
                         for article in sliced_list]

    # --------------------------------  SEND EMAIL -------------------------------#
    # Format subject to include 🔺 or 🔻 symbols depending on whether the price went up or down
    if percentage_difference >= 0:
        subject = STOCK + ": \u25b2" + "{:0.2f}".format(
            abs(percentage_difference)) + "%"
    else:
        subject = STOCK + ": \u25bc" + "{:0.2f}".format(
            abs(percentage_difference)) + "%"

    # Compose main body of email
    email_body = f"Here are the {articles_to_get} main articles of the day: \n\n" + '\n\n'.join(article_formatted)

    # Send the email
    with smtplib.SMTP(EMAIL_PROVIDER, 587) as connection:
        connection.starttls()
        connection.login(user=MY_EMAIL, password=MY_PASS)
        connection.sendmail(
            from_addr=MY_EMAIL,
            to_addrs=MY_EMAIL,
            msg=f"Subject:{subject}\n\n{email_body}".encode('UTF-8')
        )
