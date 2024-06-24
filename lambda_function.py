import json
import boto3
import os
import time

dynamodb = boto3.resource('dynamodb')
table_name = os.getenv('DYNAMODB_TABLE')
table = dynamodb.Table(table_name)
sns = boto3.client('sns')
topic_arn = os.getenv('SNS_TOPIC_ARN')

def lambda_handler(event, context):
    # Assuming event contains the game result data
    game_result = json.loads(event['body'])
    game_id = game_result['game_id']
    player1 = game_result['player1']
    player2 = game_result['player2']
    winner = game_result['winner']

    # Store game result in DynamoDB
    table.put_item(Item={
        'GameId': game_id,
        'Player1': player1,
        'Player2': player2,
        'Winner': winner,
        'Timestamp': int(time.time())
    })

    # Publish to SNS
    message = f"The game between {player1} and {player2} has ended. Winner: {winner}"
    sns.publish(TopicArn=topic_arn, Message=message)

    return {
        'statusCode': 200,
        'body': json.dumps('Game result stored and notification sent.')
    }
