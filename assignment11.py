import requests
import json
import datetime
import os
import csv
import time

def make_request(api_endpoint, data):
    """Make a request to the API and handle potential retries for bank outages."""
    retries = 0
    max_retries = 5
    backoff_factor = 1  # Seconds to wait, will increase exponentially

    while retries < max_retries:
        response = requests.post(api_endpoint, json=data)
        response_data = response.json()

        if response.status_code == 503 and response_data.get('message') == 'Bank Not Available':
            print(f"Error detected: {response_data['message']} - retrying in {backoff_factor} sec.")
            time.sleep(backoff_factor)
            backoff_factor *= 2  # Increase the backoff factor exponentially
            retries += 1
        else:
            return response_data

    return {"message": "Failed after retries", "status": "failure"}

def simulate_transactions(api_endpoint, csv_file_path):
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            transaction_data = {
                'bank': row['patient_bank'],
                'merchant_name': row['clinic_name'],
                'merchant_token': 'clinic_token',  # Assuming a unique token per clinic
                'cc_num': row['patient_card_number'],
                'card_type': 'Credit',  # Assuming credit type
                'amount': row['charge_amount']
            }

            response_data = make_request(api_endpoint, transaction_data)
            print(f"Transaction response: {response_data}")

if __name__ == '__main__':
    api_endpoint = 'https://ecwrvf6xqytiy5d7psnk2lng3q0fynzm.lambda-url.us-east-2.on.aws/'
    csv_file_path = 'data.csv'
    simulate_transactions(api_endpoint, csv_file_path)
