output "lambda_role_arn" {
  description = "The ARN of the Lambda function's IAM role"
  value = module.lambda_function_alb.lambda_role_arn
}