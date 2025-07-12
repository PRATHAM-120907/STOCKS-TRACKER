import requests
from twilio.rest import Client

STOCK_NAME = "TSLA"# CAN CHANGE NAME AS THE STOCK NAME OF IT
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

STOCK_API_KEY = "IJU17FVUXNQVSPT3"
NEWS_API_KEY = "8f6a132b8f804c99bf0b681418986b7a"

# Twilio (replace with your actual Twilio credentials)
TWILIO_SID = "TWILIO STD CODE"# GET THIS BY THE TWILIO WEBSITE
TWILIO_AUTH_TOKEN = "TOKEN" # GET THIS BY THE TWILIO WEBSITE
TWILIO_PHONE_NUMBER = "your_twilio_phone_number"# GET THIS BY THE TWILIO WEBSITE
MY_PHONE_NUMBER = "your_verified_number"# YOUR VERIFIED NUMBER 

# -------- STEP 1: Get stock data ------------
stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": STOCK_API_KEY
}

response = requests.get(STOCK_ENDPOINT, params=stock_params)
data = response.json()["Time Series (Daily)"]
data_list = [value for (date, value) in data.items()]

# Yesterday and day before
yesterday_data = data_list[0]
day_before_yesterday_data = data_list[1]

yesterday_price = float(yesterday_data["4. close"])
day_before_price = float(day_before_yesterday_data["4. close"])

# Difference and percentage change
difference = abs(yesterday_price - day_before_price)
diff_percent = (difference / yesterday_price) * 100

# -------- STEP 2: Get news if >5% change --------
if diff_percent > 5:
    news_params = {
        "apiKey": NEWS_API_KEY,
        "qInTitle": COMPANY_NAME
    }
    news_response = requests.get(NEWS_ENDPOINT, params=news_params)
    articles = news_response.json()["articles"]
    
    # -------- STEP 3: Slice top 3 articles --------
    top_articles = articles[:3]

    # Emoji for direction
    emoji = "🔺" if yesterday_price > day_before_price else "🔻"

    # -------- STEP 4: Format articles --------
    formatted_articles = [
        f"{STOCK_NAME}: {emoji}{round(diff_percent)}%\nHeadline: {article['title']}\nBrief: {article['description']}"
        for article in top_articles
    ]

    # -------- STEP 5: Send SMS using Twilio --------
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

    for article_msg in formatted_articles:
        message = client.messages.create(
            body=article_msg,
            from_=TWILIO_PHONE_NUMBER,
            to=MY_PHONE_NUMBER
        )
        print(message.status)
