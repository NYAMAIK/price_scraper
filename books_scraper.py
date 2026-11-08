import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import json

url = "https://books.toscrape.com/"

try:
    response = requests.get(url, timeout=20)
    response.raise_for_status()

    print("Website connected successfully!")
    print("Status code:", response.status_code)

except requests.exceptions.RequestException as error:
    print("Connection failed:", error)
    exit()

book_data = []

page_urls = [
    "https://books.toscrape.com/",
    "https://books.toscrape.com/catalogue/page-2.html"
]

try:
    for url in page_urls:

        response = requests.get(url, timeout=20)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        books = soup.find_all("article", class_="product_pod")

        print("Books found on this page:", len(books))

        for book in books:

            title = book.h3.a["title"]

            price_text = book.find("p", class_="price_color").text

            price = float(price_text.replace("Â", "").replace("£", "").strip())

            book_data.append({
                "Title": title,
                "Price_GBP": price
            })

    df = pd.DataFrame(book_data)

    print("\nAll scraped books:")
    print(df)

    print("\nTotal books collected:", len(df))

except requests.exceptions.RequestException as error:
    print("Connection failed:", error)

print("\nTotal books collected:", len(df))


df.to_csv("books_data.csv", index=False)

print("Data successfully saved to CSV!")


api_url = "https://open.er-api.com/v6/latest/GBP"

try:
    exchange_response = requests.get(api_url, timeout=20)

    exchange_response.raise_for_status()

    exchange_data = exchange_response.json()
    if exchange_data["result"] != "success":
        print("Currency API did not return a successful result.")
        exit()

    gbp_to_kes = exchange_data["rates"]["KES"]

    print("GBP to KES exchange rate:", gbp_to_kes)

except requests.exceptions.RequestException as error:
    print("Currency API connection failed:", error)
    exit()

df["Price_KES"] = df["Price_GBP"] * gbp_to_kes


df["Price_KES"] = df["Price_KES"].round(2)

print("\nBooks with converted prices:")
print(df)


df.to_csv("books_converted.csv", index=False)


df.to_json("books_converted.json", orient="records", indent=4)

print("Converted data saved successfully!")


chart_data = df.head(20)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

axes[0].bar(chart_data["Title"], chart_data["Price_GBP"])
axes[0].set_title("Book Prices in GBP")
axes[0].set_ylabel("Price (£)")
axes[0].tick_params(axis="x", rotation=90)

axes[1].bar(chart_data["Title"], chart_data["Price_KES"])
axes[1].set_title("Book Prices in KES")
axes[1].set_ylabel("Price (KES)")
axes[1].tick_params(axis="x", rotation=90)

plt.tight_layout()
plt.show()