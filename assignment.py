import requests
import json
import datetime
import os
import csv
import boto3

# Get absolute path to current directory
current_directory = os.path.abspath(os.path.dirname(__file__))

# Specify absolute path for CSV file
csv_file_path = os.path.join(current_directory, 'data.csv')

# Specify absolute path for log file
log_file_path = os.path.join(current_directory, 'transaction_log.txt')

# Make HTTP POST requests to the Lambda function
api_endpoint = 'https://ecwrvf6xqytiy5d7psnk2lng3q0fynzm.lambda-url.us-east-2.on.aws/'

# Read data from CSV file
with open(csv_file_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # Standardized JSON object
        timestamp = str(datetime.datetime.now())
        myobj = {
            'bank': row['bank'],
            'merchant_name': row['merchant_name'],
            'merchant_token': row['merchant_token'],
            'cc_num': row['cc_num'],
            'card_type': row['card_type'],
            'amount': row['amount']
        }

        # Make HTTP POST request
        response = requests.post(api_endpoint, json=myobj)
        response_data = response.json()
        
        # Append response to log file
        with open(log_file_path, 'a') as f:
            f.write(json.dumps(response_data) + '\n')