
# Lambda Function (store package locally)
module "lambda_function" {
  source = "terraform-aws-modules/lambda/aws"

  function_name = "my-lambda1"
  description   = "My awesome lambda function"
  handler       = "awesome-lambda.lambda_handler"
  runtime       = "python3.12"

  source_path = "${path.module}/function"
  tags = {
    Name = "my-lambda1"
  }
}