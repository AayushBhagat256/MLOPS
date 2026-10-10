# Private Elastic Container Registry (ECR) for the FastAPI container
resource "aws_ecr_repository" "mlops_repo" {
  name                 = var.app_name
  image_tag_mutability = "MUTABLE"

  # Best practice: automatic vulnerability scanning on push
  image_scanning_configuration {
    scan_on_push = true
  }

  # Server-side encryption at rest
  encryption_configuration {
    encryption_type = "AES256"
  }
}

# Lifecycle policy: retain only the latest 10 images to prevent unbounded storage costs
resource "aws_ecr_lifecycle_policy" "repo_policy" {
  repository = aws_ecr_repository.mlops_repo.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep only the 10 most recent images"
        selection = {
          tagStatus   = "any"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 30
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}
