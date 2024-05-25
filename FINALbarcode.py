import requests
import json
import sys
import csv
from pymongo import MongoClient

client = MongoClient('mongodb+srv://raf322:Spark0702@cluster0.fhcw5oz.mongodb.net/')
db = client.cooleye
collection = db.barcodes


def get_barcode():
    barcode_input = input("Scan a barcode: ")
    print("Test1")
    return barcode_input

program_status = True
while program_status:
    barcode = get_barcode()
    print("Beginning of while loop")
    # set up the request parameters
    params = {
    'api_key': 'DA2E881C539445868AD19CE7489198C2',
      'type': 'product',
      'gtin': barcode,
      'output': 'csv',
      'csv_fields': 'product.title',
    }
    # make the http GET request to BlueCart API
    api_result = requests.get('https://api.bluecartapi.com/request', params)

    # print the JSON response from BlueCart API
    data = api_result.content.decode('utf-8')

    print("We made it to place 1") 
    first_line_break = data.find('\n')
    
    if first_line_break != -1:
        # Print everything after the first line break
        #print("maybe here?")
        name = data[first_line_break+1:]
        #print(data)
    print(data[first_line_break+1:])
    send_data = {
        "barcode": barcode,
        "item name": name
    }
 
    print("We made it to end")
    
    collection.insert_one(send_data)    
    #db.collection.insert(send_data)
    #print(send_data.inserted_id)
    program_status = False
