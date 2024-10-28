#
## Lambda Function (store package locally)
#module "lambda_function_alb" {
#  source = "terraform-aws-modules/lambda/aws"
#  version = "7.10.0"
#  function_name = "my-lambda1"
#  description   = "My awesome lambda function"
#  handler       = "awesome-lambda.lambda_handler"
#  runtime       = "python3.12"
#
#  source_path = "${path.module}/function"
#  tags = {
#    Name = "my-lambda1"
#  }
#}
