# S3 访问策略
## 基于资源的策略（Resource-based Policies）

## 基于角色的策略（Role-based Policies）：


## 区别
在AWS中，基于资源的策略和基于角色的策略在JSON文档结构上的主要区别之一是是否包含`Principal`字段。

1. **基于资源的策略（Resource-based Policies）**：
    - **包含`Principal`字段**：基于资源的策略直接附加到资源上（如S3存储桶、SNS主题），因此需要指定哪些主体（用户、角色、账户）可以访问该资源。这是通过`Principal`字段来实现的。
    - **示例**：
      ```json
      {
        "Version": "2012-10-17",
        "Statement": [
          {
            "Effect": "Allow",
            "Principal": {
              "AWS": "arn:aws:iam::123456789012:user/ExampleUser"
            },
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::example-bucket/*"
          }
        ]
      }
      ```

2. **基于角色的策略（Role-based Policies）**：
    - **不包含`Principal`字段**：基于角色的策略附加到IAM角色上，定义该角色可以对哪些资源执行哪些操作。因为策略是附加到角色上的，所以不需要指定`Principal`。
    - **示例**：
      ```json
      {
        "Version": "2012-10-17",
        "Statement": [
          {
            "Effect": "Allow",
            "Action": "s3:ListBucket",
            "Resource": "arn:aws:s3:::example-bucket"
          }
        ]
      }
      ```

因此，`Principal`字段的存在与否是区分这两种策略的一个关键因素。基于资源的策略需要明确指定允许访问的主体，而基于角色的策略则不需要，因为它们已经与特定的IAM角色绑定。
