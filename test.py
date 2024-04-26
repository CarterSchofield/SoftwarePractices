import json
import boto3
from decimal import Decimal

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
merchant_table_name = 'Merchants'  # Replace with your DynamoDB table name for merchants
bank_table_name = 'banks'  # Replace with your DynamoDB table name for banks

merchant_table = dynamodb.Table(merchant_table_name)
bank_table = dynamodb.Table(bank_table_name)

def lambda_handler(event, context):
    # Parse the request body JSON data
    if 'body' in event and event['body']:
        body = json.loads(event['body'])
        
        if 'merchant_name' in body and 'merchant_token' in body:
            merchant_name = body['merchant_name']
            merchant_token = body['merchant_token']
            
            # Query DynamoDB to check if MerchantName and Token exist
            merchant_response = merchant_table.get_item(
                Key={
                    'MerchantName': merchant_name,
                    'Token': merchant_token
                }
            )
            
            # Check if the merchant is authorized
            if 'Item' in merchant_response:
                # Get the card details from the request
                if 'cc_num' in body and 'card_type' in body:
                    cc_num = body['cc_num']
                    card_type = body['card_type']
                    
                    # Query DynamoDB to get bank details
                    bank_response = bank_table.get_item(
                        Key={
                            'BankName': body['bank'],
                            'AccountNum': cc_num
                        }
                    )
                    
                    # Check if bank details exist
                    if 'Item' in bank_response:
                        bank_item = bank_response['Item']
                        if card_type == 'Credit':
                            available_credit = Decimal(bank_item.get('CreditLimit', '0')) - Decimal(bank_item.get('CreditUsed', '0'))
                            amount = Decimal(body['amount'])
                            if amount <= available_credit:
                                # Update bank table with new credit used
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
                                return {
                                    "statusCode": 200,
                                    "body": json.dumps({"message": "Approved"})
                                }
                            else:
                                return {
                                    "statusCode": 403,
                                    "body": json.dumps({"message": "Declined. Insufficient Funds"})
                                }
                        elif card_type == 'Debit':
                            available_balance = Decimal(bank_item.get('Balance', '0'))
                            amount = Decimal(body['amount'])
                            if amount <= available_balance:
                                # Update bank table with new balance
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
                                return {
                                    "statusCode": 200,
                                    "body": json.dumps({"message": "Approved"})
                                }
                            else:
                                return {
                                    "statusCode": 403,
                                    "body": json.dumps({"message": "Declined. Insufficient Funds"})
                                }
                        else:
                            return {
                                "statusCode": 400,
                                "body": json.dumps({"message": "Invalid card type. Must be 'Credit' or 'Debit'"})
                            }
                    else:
                        return {
                            "statusCode": 404,
                            "body": json.dumps({"message": "Error - Bad Bank or Account Number"})
                        }
                else:
                    return {
                        "statusCode": 400,
                        "body": json.dumps({"message": "Card number and card type are required in the request body"})
                    }
            else:
                return {
                    "statusCode": 401,
                    "body": json.dumps({"message": "Merchant not Authorized"})
                }
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({"message": "MerchantName and MerchantToken are required in the request body"})
            }
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Request body is missing"})
        }
