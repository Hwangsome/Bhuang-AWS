module "sns-success" {
  source  = "terraform-aws-modules/sns/aws"
  version = ">= 5.0"

  name = "lambda-success"

  topic_policy_statements = {
    sqs = {
      sid = "SQSSubscribe"
      actions = [
        "sns:Subscribe",
        "sns:Receive",
      ]

      principals = [{
        type        = "AWS"
        identifiers = ["*"]
      }]

      conditions = [{
        test     = "StringLike"
        variable = "sns:Endpoint"
        values   = [module.sqs-success.queue_arn]
      }]
    }
  }

  subscriptions = {
    sqs = {
      protocol = "sqs"
      endpoint = module.sqs-success.queue_arn
    }
  }

  tags = {
    Environment = "dev"
  }
}


module "sns-fail" {
  source  = "terraform-aws-modules/sns/aws"
  version = ">= 5.0"

  name = "lambda-fail"

  topic_policy_statements = {
    sqs = {
      sid = "SQSSubscribe"
      actions = [
        "sns:Subscribe",
        "sns:Receive",
      ]

      principals = [{
        type        = "AWS"
        identifiers = ["*"]
      }]

      conditions = [{
        test     = "StringLike"
        variable = "sns:Endpoint"
        values   = [module.sqs-fail.queue_arn]
      }]
    }
  }

  subscriptions = {
    sqs = {
      protocol = "sqs"
      endpoint = module.sqs-fail.queue_arn
    }
  }

  tags = {
    Environment = "dev"
  }
}





