import requests
import csv
import io
from pymongo import MongoClient

# Securely configure your MongoDB connection string
client = MongoClient('your_mongodb_connection_string')
db = client.cooleye
collection = db.barcodes

def get_barcode():
    barcode_input = input("Scan a barcode: ")
    return barcode_input

def fetch_product_data(barcode):
    params = {
        'api_key': 'YOUR_API_KEY',
        'type': 'product',
        'gtin': barcode,
        'output': 'csv',
        'csv_fields': 'request.gtin,product.title,product.upc',
    }

    try:
        api_result = requests.get('https://api.bluecartapi.com/request', params)
        api_result.raise_for_status()  # Raises an error for bad responses

        csv_reader = csv.DictReader(io.StringIO(api_result.text))
        for row in csv_reader:
            return row  # Assuming only one row of interest

    except requests.exceptions.RequestException as e:
        print(f"Error fetching product data: {e}")

def main():
    program_status = True
    while program_status:
        barcode = get_barcode()
        product_data = fetch_product_data(barcode)
        
        if product_data:
            print(product_data)
            collection.insert_one(product_data)
        else:
            print("Failed to fetch product data or parse CSV.")

if __name__ == "__main__":
    main()
