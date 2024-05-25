import json

def get_barcode():
    barcode_input = input("Scan a barcode: ")
    return barcode_input

class BarcodeVector:
    def __init__(self):
        self.data = []

    def scan_and_add(self):
        barcode_input = get_barcode()
        item_info = self.search_barcode_in_json(barcode_input)
        if item_info:
            self.data.append(item_info)
        else:
            print("Barcode not found in JSON file.")

    def search_barcode_in_json(self, barcode):
        try:
            with open('example.json', 'r') as file:
                data = json.load(file)

            # If the data is a list, iterate through it
                if isinstance(data, list):
                    for item in data:
                        if item['barcode'] == barcode:
                            return {
                                'name': item['name'],
                                'days': item['days']
                            }
            # If the data is a dictionary, check it directly
                elif isinstance(data, dict):
                    if data['barcode'] == barcode:
                        return {
                            'name': data['name'],
                            'days': data['days']
                        }
        except FileNotFoundError:
            print("JSON file not found.")
        except json.JSONDecodeError:
            print("Error decoding JSON.")
        return None


    def get_vector(self):
        return self.data

barcode_vector = BarcodeVector()

while True:
    barcode_vector.scan_and_add()
    print("Current vector:", barcode_vector.get_vector())
