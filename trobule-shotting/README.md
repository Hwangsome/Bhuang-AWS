# ec2 注册到 target group的时候健康检查失败
tg配置的健康检查是
```shell
health_check {
    healthy_threshold   = 3
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/"  # 指定您服务的健康检查路径
    protocol            = "HTTP"
  }
```
进入ec2,发现403，所以健康检查失败
```shell
curl -I http://localhost/
HTTP/1.1 403 Forbidden
Date: Wed, 15 Jan 2025 09:03:35 GMT
Server: Apache/2.4.62 (Amazon Linux)
Last-Modified: Mon, 11 Jun 2007 18:53:14 GMT
ETag: "2d-432a5e4a73a80"
Accept-Ranges: bytes
Content-Length: 45
Content-Type: text/html; charset=UTF-8
```

需要修改为
```shell
health_check {
    healthy_threshold   = 3
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/"  # 指定您服务的健康检查路径
    protocol            = "TCP"
  }
```