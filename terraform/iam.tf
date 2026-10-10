# 1. IAM Role allowing App Runner to authenticate and pull images from ECR
resource "aws_iam_role" "apprunner_ecr_access" {
  name        = "${var.app_name}-apprunner-ecr-access"
  description = "Allows AWS App Runner to pull container images from private ECR repositories"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "build.apprunner.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# Attach AWS managed policy for ECR access to App Runner
resource "aws_iam_role_policy_attachment" "apprunner_ecr_access_attachment" {
  role       = aws_iam_role.apprunner_ecr_access.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess"
}

# 2. IAM Role for running container instances (Instance Role)
resource "aws_iam_role" "apprunner_instance_role" {
  name        = "${var.app_name}-apprunner-instance-role"
  description = "Runtime IAM role assumed by the container running inside App Runner"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "tasks.apprunner.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}
