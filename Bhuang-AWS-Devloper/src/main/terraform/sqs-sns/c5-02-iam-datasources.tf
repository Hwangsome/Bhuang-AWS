# 生成 JSON 格式的 IAM 策略文档，以便与需要策略文档的资源一起使用
data "aws_iam_policy_document" "sns_policy" {
  statement {
    sid = "1"

    actions = [
      "sns:Publish"
    ]

#    表示允许 Lambda 函数发布到指定的 SNS 主题 （lambda-xxx）
    resources = [
      "arn:aws:sns:us-west-2:058264261029:lambda-*"
    ]
  }
}