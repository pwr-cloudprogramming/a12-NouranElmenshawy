import boto3
from botocore.exceptions import ClientError

USER_POOL_ID = 'us-east-1_5Zp4VGVxW'  # Replace with your actual User Pool ID
CLIENT_ID = 'ivmmhv55tccpbeb23lb3i5jlm'  # Replace with your actual Client ID
REGION = 'us-east-1'

cognito_client = boto3.client('cognito-idp', region_name=REGION)

def register_user(username, password, email):
    try:
        response = cognito_client.sign_up(
            ClientId=CLIENT_ID,
            Username=username,
            Password=password,
            UserAttributes=[
                {'Name': 'email', 'Value': email}
            ]
        )
        return response
    except ClientError as e:
        return {'error': e.response['Error']['Message']}

def confirm_user(username, code):
    try:
        response = cognito_client.confirm_sign_up(
            ClientId=CLIENT_ID,
            Username=username,
            ConfirmationCode=code
        )
        return response
    except ClientError as e:
        return {'error': e.response['Error']['Message']}

def login_user(username, password):
    try:
        response = cognito_client.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        return response
    except ClientError as e:
        return {'error': e.response['Error']['Message']}
