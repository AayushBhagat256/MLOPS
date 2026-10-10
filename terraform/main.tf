provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.app_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# 1. Auto-scaling configuration for App Runner
resource "aws_apprunner_auto_scaling_configuration_version" "auto_scaling" {
  auto_scaling_configuration_name = "${var.app_name}-autoscaling"

  min_size        = var.auto_scaling_min_size
  max_size        = var.auto_scaling_max_size
  max_concurrency = var.auto_scaling_max_concurrency
}

# 2. AWS App Runner Service
resource "aws_apprunner_service" "api_service" {
  service_name = "${var.app_name}-${var.environment}"

  auto_scaling_configuration_arn = aws_apprunner_auto_scaling_configuration_version.auto_scaling.arn

  source_configuration {
    authentication_configuration {
      access_role_arn = aws_iam_role.apprunner_ecr_access.arn
    }

    image_repository {
      image_identifier      = "${aws_ecr_repository.mlops_repo.repository_url}:${var.image_tag}"
      image_repository_type = "ECR"

      image_configuration {
        port = tostring(var.container_port)

        runtime_environment_variables = {
          ENVIRONMENT = var.environment
          PORT        = tostring(var.container_port)
        }
      }
    }

    # Automatically deploy when a new image is pushed to ECR with this tag
    auto_deployments_enabled = true
  }

  instance_configuration {
    cpu               = var.cpu
    memory            = var.memory
    instance_role_arn = aws_iam_role.apprunner_instance_role.arn
  }

  health_check_configuration {
    protocol            = "HTTP"
    path                = "/api/v1/health"
    interval            = 10
    timeout             = 5
    healthy_threshold   = 1
    unhealthy_threshold = 5
  }

  depends_on = [
    aws_iam_role_policy_attachment.apprunner_ecr_access_attachment
  ]
}
