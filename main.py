import requests
import datetime
import smtplib
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk

# ---------------------------- CONSTANTS ------------------------------- #
FONT = ("Arial", 10)
DESCRIPTION_FONT = ("Arial", 10, "italic")
IMAGE_WIDTH = 460
IMAGE_HEIGHT = 249


# ------------------------------- GET INPUTS FROM GUI FUNCTION-------------------------------#
def get_inputs_from_GUI():
    global email_address, email_password, stock_name_get, company_name_get, api_key_stock, api_key_news, stock_endpoint, \
        news_endpoint, email_provider, email_port
    email_address = email_input.get()
    email_password = password_input.get()
    stock_name_get = stock_name_input.get()
    company_name_get = company_name_input.get()
    api_key_stock = stock_API_key_input.get()
    api_key_news = news_API_key_input.get()

    stock_endpoint = "https://www.alphavantage.co/query"
    news_endpoint = "https://newsapi.org/v2/everything"

    provider = email_address[email_address.find('@'):]
    if provider == "@gmail.com":
        email_provider = "smtp.gmail.com"
        email_port = 587
    elif provider == "@yahoo.com":
        email_provider = "smtp.yahoo.com"
        email_port = 465
    else:
        messagebox.showinfo(title="error", message="Give Valid Email Provider: gmail.com or yahoo.com")
        return -1


# ------------------------------- STOCK PRICE FUNCTION -------------------------------#
def get_stock_price_API():
    global percentage_difference
    # Get the daily time series of the stock through the API
    parameters_stock = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": stock_name_get,
        "apikey": api_key_stock
    }

    try:
        stock_data = requests.get(stock_endpoint, params=parameters_stock)
        stock_data.raise_for_status()
    except requests.exceptions.HTTPError as err:
        messagebox.showinfo(title=f"API key error", message=err)
        return -1

    # Check if data have been read correctly
    try:
        stock_data = stock_data.json()["Time Series (Daily)"]
    except KeyError:
        messagebox.showinfo(title="API value error",
                            message=f"Stock {stock_name_get} does not exist in https://www.alphavantage.co/query")
        return -1

    # Create a list with the data
    price_list = [value for (key, value) in stock_data.items()]

    # Find the closing prices for yesterday and the day before yesterday
    price_of_yesterday = float(price_list[0]["4. close"])
    price_of_the_day_before_yesterday = float(price_list[1]["4. close"])

    # Calculate the difference in price between yesterday and the day before yesterday
    percentage_difference = (price_of_yesterday - price_of_the_day_before_yesterday) \
                            / price_of_the_day_before_yesterday * 100


# -------------------------------  STOCK NEWS FUNCTION-------------------------------#
def get_stock_news_API():
    global articles_to_get, articles_formatted
    # Get today's articles
    today = datetime.datetime.now()
    day_of_the_article = str(today).split()[0]
    parameters_news = {
        "q": company_name_get,
        "from": day_of_the_article,
        "to": day_of_the_article,
        "sortBy": "popularity",
        "apiKey": api_key_news
    }

    try:
        news_data = requests.get(news_endpoint, params=parameters_news)
        news_data.raise_for_status()
    except requests.exceptions.HTTPError as err:
        messagebox.showinfo(title="API key error", message=err)
        return -1

    total_num_articles = news_data.json()['totalResults']

    # Check if there are at least 3 articles
    if total_num_articles >= 3:
        articles_to_get = 3
    else:
        articles_to_get = total_num_articles

    # Create a list with the first 3 articles
    sliced_list = news_data.json()['articles'][slice(articles_to_get)]
    articles_formatted = [
        f"\u2022 Headline: {article['title']}. \n\u2022 Brief:{article['description']} \n\u2022 URL: {article['url']}"
        for article in sliced_list]


# -------------------------------- SEND EMAIL FUNCTION -------------------------------#
def send_email():

    # Format subject to include 🔺 or 🔻 symbols depending on whether the price went up or down
    if percentage_difference >= 0:
        subject = stock_name_get + ": \u25b2" + "{:0.2f}".format(
            abs(percentage_difference)) + "%"
    else:
        subject = stock_name_get + ": \u25bc" + "{:0.2f}".format(
            abs(percentage_difference)) + "%"

    # Compose main body of email
    email_body = f"Here are the {articles_to_get} main articles of the day for {company_name_get}:" \
                 f" \n\n" + '\n\n'.join(articles_formatted)

    # Send the email
    try:
        with smtplib.SMTP(email_provider, email_port) as connection:
            connection.starttls()
            connection.login(user=email_address, password=email_password)
            connection.sendmail(
                from_addr=email_address,
                to_addrs=email_address,
                msg=f"Subject:{subject}\n\n{email_body}".encode('UTF-8')
            )
    except smtplib.SMTPAuthenticationError as err:
        messagebox.showinfo(title="Email or pass error", message=err)
        return -1


def main():

    if get_inputs_from_GUI() == -1:
        return None

    if get_stock_price_API() == -1:
        return None

    if get_stock_news_API() == -1:
        return None

    if send_email() == -1:
        return None


# ------------------------------- UI SETUP -------------------------------#
# Window
window = Tk()
window.title('Stock News')
window.config(padx=50, pady=25)

# Canvas and image
load = Image.open("logo.jpg")
resize_image = load.resize((IMAGE_WIDTH, IMAGE_HEIGHT))
final_image = ImageTk.PhotoImage(resize_image)

canvas = Canvas(width=IMAGE_WIDTH, height=IMAGE_HEIGHT, borderwidth=0, highlightthickness=0)
canvas.create_image(IMAGE_WIDTH / 2, IMAGE_HEIGHT / 2, image=final_image)
canvas.grid(column=0, row=0, columnspan=3, pady=25)

# Input labels
email = Label(text="Email: ")
email.config(font=FONT)
email.grid(column=0, row=1)

password = Label(text="Password: ")
password.config(font=FONT)
password.grid(column=0, row=2)

stock_name = Label(text="Stock name: ")
stock_name.config(font=FONT)
stock_name.grid(column=0, row=3)

company_name = Label(text="Company name: ")
company_name.config(font=FONT)
company_name.grid(column=0, row=4)

stock_API_key = Label(text="Stock API key: ")
stock_API_key.config(font=FONT)
stock_API_key.grid(column=0, row=5)

news_API_key = Label(text="News API key: ")
news_API_key.config(font=FONT)
news_API_key.grid(column=0, row=6)

# Description labels
email_details = Label(text="gmail.com or yahoo.com")
email_details.config(font=DESCRIPTION_FONT)
email_details.grid(column=2, row=1, sticky="W")

password_details = Label(text="your email app password")
password_details.config(font=DESCRIPTION_FONT)
password_details.grid(column=2, row=2, sticky="W")

stock_name_details = Label(text="from https://www.alphavantage.co/")
stock_name_details.config(font=DESCRIPTION_FONT)
stock_name_details.grid(column=2, row=3, sticky="W")

company_name_details = Label(text="from https://newsapi.org/")
company_name_details.config(font=DESCRIPTION_FONT)
company_name_details.grid(column=2, row=4, sticky="W")

stock_API_key_details = Label(text="from https://www.alphavantage.co/")
stock_API_key_details.config(font=DESCRIPTION_FONT)
stock_API_key_details.grid(column=2, row=5, sticky="W")

news_API_key_details = Label(text="from https://newsapi.org/")
news_API_key_details.config(font=DESCRIPTION_FONT)
news_API_key_details.grid(column=2, row=6, sticky="W")

# Entries
email_input = Entry(width=28)
email_input.grid(column=1, row=1)
email_input.focus()

password_input = Entry(width=28)
password_input.grid(column=1, row=2)

stock_name_input = Entry(width=28)
stock_name_input.insert(0, "TSLA")
stock_name_input.grid(column=1, row=3)

company_name_input = Entry(width=28)
company_name_input.insert(0, "Tesla Inc")
company_name_input.grid(column=1, row=4)

stock_API_key_input = Entry(width=28)
stock_API_key_input.grid(column=1, row=5)

news_API_key_input = Entry(width=28)
news_API_key_input.grid(column=1, row=6)

# Button
send_news_email = Button(text="Send news email", command=main, width=30, bg='black', fg='white')
send_news_email.config(font=FONT)
send_news_email.grid(column=0, row=7, columnspan=3, pady=25)

window.mainloop()
