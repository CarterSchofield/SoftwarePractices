import json
import boto3
from decimal import Decimal
import datetime
import random  # Import for generating random numbers
#CI/CD works!

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
merchant_table_name = 'Merchants'
bank_table_name = 'banks'
transaction_table_name = 'Transactions'

merchant_table = dynamodb.Table(merchant_table_name)
bank_table = dynamodb.Table(bank_table_name)
transaction_table = dynamodb.Table(transaction_table_name)

def lambda_handler(event, context):
    transaction_status = "Error"
    transaction_details = {
        'TransactionID': str(context.aws_request_id),
        'Timestamp': datetime.datetime.now().isoformat(),
        'MerchantName': None,
        'MerchantID': None,
        'LastFourCC': None,
        'Amount': None,
        'Status': transaction_status
    }

    # Simulate bank API failure 10% of the time
    if random.randint(1, 10) == 1:
        transaction_status = "Bank Not Available"
        transaction_details['Status'] = transaction_status
        transaction_table.put_item(Item=transaction_details)
        return {
            "statusCode": 503,
            "body": json.dumps({"message": transaction_status})
        }

    if 'body' in event and event['body']:
        body = json.loads(event['body'])

        if 'merchant_name' in body and 'merchant_token' in body:
            merchant_name = body['merchant_name']
            merchant_token = body['merchant_token']

            transaction_details['MerchantName'] = merchant_name
            transaction_details['MerchantID'] = merchant_token

            merchant_response = merchant_table.get_item(
                Key={
                    'MerchantName': merchant_name,
                    'Token': merchant_token
                }
            )

            if 'Item' in merchant_response:
                if 'cc_num' in body and 'card_type' in body:
                    cc_num = body['cc_num']
                    card_type = body['card_type']
                    transaction_details['LastFourCC'] = cc_num[-4:]
                    transaction_details['Amount'] = body['amount']

                    bank_response = bank_table.get_item(
                        Key={
                            'BankName': body['bank'],
                            'AccountNum': cc_num
                        }
                    )

                    if 'Item' in bank_response:
                        bank_item = bank_response['Item']
                        if card_type == 'Credit':
                            available_credit = Decimal(bank_item.get('CreditLimit', '0')) - Decimal(bank_item.get('CreditUsed', '0'))
                            amount = Decimal(body['amount'])
                            if amount <= available_credit:
                                new_credit_used = Decimal(bank_item.get('CreditUsed', '0')) + amount
                                bank_table.update_item(
                                    Key={
                                        'BankName': body['bank'],
                                        'AccountNum': cc_num
                                    },
                                    UpdateExpression='SET CreditUsed = :new_credit_used',
                                    ExpressionAttributeValues={
                                        ':new_credit_used': new_credit_used
                                    }
                                )
                                transaction_status = "Approved"
                            else:
                                transaction_status = "Declined. Insufficient Funds"
                        elif card_type == 'Debit':
                            available_balance = Decimal(bank_item.get('Balance', '0'))
                            amount = Decimal(body['amount'])
                            if amount <= available_balance:
                                new_balance = available_balance - amount
                                bank_table.update_item(
                                    Key={
                                        'BankName': body['bank'],
                                        'AccountNum': cc_num
                                    },
                                    UpdateExpression='SET Balance = :new_balance',
                                    ExpressionAttributeValues={
                                        ':new_balance': new_balance
                                    }
                                )
                                transaction_status = "Approved"
                            else:
                                transaction_status = "Declined. Insufficient Funds"
                        else:
                            transaction_status = "Invalid card type. Must be 'Credit' or 'Debit'"
                    else:
                        transaction_status = "Error - Bad Bank or Account Number"
                else:
                    transaction_status = "Card number and card type are required in the request body"
            else:
                transaction_status = "Merchant not Authorized"
        else:
            transaction_status = "MerchantName and MerchantToken are required in the request body"
    else:
        transaction_status = "Request body is missing"

    # Log the transaction in the DynamoDB Transactions table
    transaction_details['Status'] = transaction_status
    transaction_table.put_item(Item=transaction_details)

    return {
        "statusCode": 200 if transaction_status == "Approved" else 403 if "Declined" in transaction_status else 400,
        "body": json.dumps({"message": transaction_status})
    }
