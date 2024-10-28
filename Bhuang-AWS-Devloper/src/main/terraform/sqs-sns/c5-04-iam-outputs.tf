output "sns_policy_json" {
  description = "The JSON policy document"
  value = data.aws_iam_policy_document.sns_policy.json
}

output "sns_policy_id" {
  description = "The ID of the policy document"
  value = data.aws_iam_policy_document.sns_policy.id
}

output "iam_policy_arn" {
  description = "The ARN of the SNS topic"
  value = aws_iam_policy.publish_sns_policy.arn
}