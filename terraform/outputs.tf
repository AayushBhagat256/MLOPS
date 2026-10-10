output "ecr_repository_url" {
  description = "The URL of the private ECR repository"
  value       = aws_ecr_repository.mlops_repo.repository_url
}

output "ecr_repository_arn" {
  description = "ARN of the ECR repository"
  value       = aws_ecr_repository.mlops_repo.arn
}

output "app_runner_service_url" {
  description = "Public HTTPS URL for the deployed FastAPI service"
  value       = "https://${aws_apprunner_service.api_service.service_url}"
}

output "app_runner_service_status" {
  description = "Current status of the App Runner service"
  value       = aws_apprunner_service.api_service.status
}

output "apprunner_ecr_access_role_arn" {
  description = "ARN of the IAM role used by App Runner to pull images"
  value       = aws_iam_role.apprunner_ecr_access.arn
}
