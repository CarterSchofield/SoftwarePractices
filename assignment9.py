import csv
import requests
import json
import os

def send_transaction(api_endpoint, transaction_data):
    response = requests.post(api_endpoint, json=transaction_data)
    return response.json()

def main():

    csv_file_path = 'health.csv'  # Update this with the actual path to the CSV file

    api_endpoint = 'https://ecwrvf6xqytiy5d7psnk2lng3q0fynzm.lambda-url.us-east-2.on.aws/'

    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:

            transaction_data = {
                'bank': row['patient_bank'],
                'merchant_name': row['clinic_name'],
                'merchant_token': 'your_clinic_specific_token',  # Assume a default or lookup token for the clinic
                'cc_num': row['patient_card_number'],
                'card_type': 'Credit', 
                'amount': row['charge_amount']
            }

            # Send the transaction to the API
            response_data = send_transaction(api_endpoint, transaction_data)
            print(f"Transaction response for {row['patient_name']}: {response_data}")

if __name__ == '__main__':
    main()
