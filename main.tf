provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "tic_tac_toe_bucket" {
  bucket = "tic-tac-toe-pic-bucketNE"

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["PUT", "POST"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

resource "aws_dynamodb_table" "tictactoe_scores" {
  name           = "TicTacToeScores"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "GameId"
  range_key      = "Timestamp"

  attribute {
    name = "GameId"
    type = "S"
  }

  attribute {
    name = "Timestamp"
    type = "N"
  }
}

resource "aws_iam_role" "lab_role" {
  name               = "LabRole"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy" "lab_role_policy" {
  name   = "lab_role_policy"
  role   = aws_iam_role.lab_role.id
  policy = data.aws_iam_policy_document.lab_role_policy.json
}

data "aws_iam_policy_document" "lab_role_policy" {
  statement {
    actions = [
      "s3:*",
      "dynamodb:*",
      "logs:*",
      "cloudwatch:*",
      "sns:*"
    ]

    resources = ["*"]
  }
}

resource "aws_lambda_function" "update_ranking" {
  function_name    = "UpdateRanking"
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.9"
  role             = aws_iam_role.lab_role.arn
  filename         = "lambda_function.zip"
  source_code_hash = filebase64sha256("lambda_function.zip")
  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.tictactoe_scores.name
      SNS_TOPIC_ARN  = aws_sns_topic.ranking_notifications.arn
    }
  }
}

resource "aws_api_gateway_rest_api" "tictactoe_api" {
  name        = "TicTacToeAPI"
  description = "API for TicTacToe game"
}

resource "aws_api_gateway_resource" "tictactoe_resource" {
  rest_api_id = aws_api_gateway_rest_api.tictactoe_api.id
  parent_id   = aws_api_gateway_rest_api.tictactoe_api.root_resource_id
  path_part   = "submit_game_result"
}

resource "aws_api_gateway_method" "tictactoe_method" {
  rest_api_id   = aws_api_gateway_rest_api.tictactoe_api.id
  resource_id   = aws_api_gateway_resource.tictactoe_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.tictactoe_api.id
  resource_id             = aws_api_gateway_resource.tictactoe_resource.id
  http_method             = aws_api_gateway_method.tictactoe_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.update_ranking.invoke_arn
}

resource "aws_api_gateway_deployment" "tictactoe_deployment" {
  rest_api_id = aws_api_gateway_rest_api.tictactoe_api.id
  stage_name  = "prod"
  depends_on  = [aws_api_gateway_integration.lambda_integration]
}

resource "aws_sns_topic" "ranking_notifications" {
  name = "RankingNotifications"
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.update_ranking.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.tictactoe_api.execution_arn}/*/*"
}provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "tic_tac_toe_bucket" {
  bucket = "tic-tac-toe-pic-bucket9"

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["PUT", "POST"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

resource "aws_dynamodb_table" "tictactoe_scores" {
  name           = "TicTacToeScores"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "GameId"
  range_key      = "Timestamp"

  attribute {
    name = "GameId"
    type = "S"
  }

  attribute {
    name = "Timestamp"
    type = "N"
  }
}

resource "aws_iam_role" "lab_role" {
  name               = "LabRole"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

data "aws_iam_policy_document" "assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy" "lab_role_policy" {
  name   = "lab_role_policy"
  role   = aws_iam_role.lab_role.id
  policy = data.aws_iam_policy_document.lab_role_policy.json
}

data "aws_iam_policy_document" "lab_role_policy" {
  statement {
    actions = [
      "s3:*",
      "dynamodb:*",
      "logs:*",
      "cloudwatch:*",
      "sns:*"
    ]

    resources = ["*"]
  }
}

resource "aws_lambda_function" "update_ranking" {
  function_name    = "UpdateRanking"
  handler          = "lambda_function.lambda_handler"
  runtime          = "python3.9"
  role             = aws_iam_role.lab_role.arn
  filename         = "lambda_function.zip"
  source_code_hash = filebase64sha256("lambda_function.zip")
  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.tictactoe_scores.name
      SNS_TOPIC_ARN  = aws_sns_topic.ranking_notifications.arn
    }
  }
}

resource "aws_api_gateway_rest_api" "tictactoe_api" {
  name        = "TicTacToeAPI"
  description = "API for TicTacToe game"
}

resource "aws_api_gateway_resource" "tictactoe_resource" {
  rest_api_id = aws_api_gateway_rest_api.tictactoe_api.id
  parent_id   = aws_api_gateway_rest_api.tictactoe_api.root_resource_id
  path_part   = "submit_game_result"
}

resource "aws_api_gateway_method" "tictactoe_method" {
  rest_api_id   = aws_api_gateway_rest_api.tictactoe_api.id
  resource_id   = aws_api_gateway_resource.tictactoe_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.tictactoe_api.id
  resource_id             = aws_api_gateway_resource.tictactoe_resource.id
  http_method             = aws_api_gateway_method.tictactoe_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.update_ranking.invoke_arn
}

resource "aws_api_gateway_deployment" "tictactoe_deployment" {
  rest_api_id = aws_api_gateway_rest_api.tictactoe_api.id
  stage_name  = "prod"
  depends_on  = [aws_api_gateway_integration.lambda_integration]
}

resource "aws_sns_topic" "ranking_notifications" {
  name = "RankingNotifications"
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.update_ranking.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.tictactoe_api.execution_arn}/*/*"
}
