# 创建 aws 的 policy resource
resource "aws_iam_policy" "publish_sns_policy" {
  name   = "publish_sns_policy"
  policy = data.aws_iam_policy_document.sns_policy.json
}

# 将policy attach 到 role 上
# lambda 需要这个role 来执行 sns publish
resource "aws_iam_role_policy_attachment" "lambda_sns" {
  role = module.lambda_function_alb.lambda_role_name
  policy_arn = aws_iam_policy.publish_sns_policy.arn
}