module "sqs-success" {
  source = "terraform-aws-modules/sqs/aws"

  name = "lambda-success"

  create_queue_policy = true
  queue_policy_statements = {
    sns = {
      sid     = "SNSPublish"
      actions = ["sqs:SendMessage"]

      principals = [
        {
          type        = "Service"
          identifiers = ["sns.amazonaws.com"]
        }
      ]

      conditions = [{
        test     = "ArnEquals"
        variable = "aws:SourceArn"
        values   = [module.sns-success.topic_arn]
      }]
    }
  }

  tags = {
    Environment = "dev"
  }
}

module "sqs-fail" {
  source = "terraform-aws-modules/sqs/aws"

  name = "lambda-fail"

  create_queue_policy = true
  queue_policy_statements = {
    sns = {
      sid     = "SNSPublish"
      actions = ["sqs:SendMessage"]

      principals = [
        {
          type        = "Service"
          identifiers = ["sns.amazonaws.com"]
        }
      ]

      conditions = [{
        test     = "ArnEquals"
        variable = "aws:SourceArn"
        values   = [module.sns-fail.topic_arn]
      }]
    }
  }

  tags = {
    Environment = "dev"
  }
}