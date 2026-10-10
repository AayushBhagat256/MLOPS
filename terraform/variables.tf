variable "aws_region" {
  type        = string
  description = "AWS deployment region"
  default     = "us-east-1"
}

variable "app_name" {
  type        = string
  description = "Application and resource naming prefix"
  default     = "iris-mlops-api"
}

variable "environment" {
  type        = string
  description = "Environment identifier (e.g. dev, staging, production)"
  default     = "production"
}

variable "container_port" {
  type        = number
  description = "Port exposed by the FastAPI container"
  default     = 8000
}

variable "cpu" {
  type        = string
  description = "Number of CPU units reserved for each instance (e.g., 1024 = 1 vCPU)"
  default     = "1024"
}

variable "memory" {
  type        = string
  description = "Amount of memory in MB reserved for each instance (e.g., 2048 = 2 GB)"
  default     = "2048"
}

variable "auto_scaling_min_size" {
  type        = number
  description = "Minimum number of App Runner instances"
  default     = 1
}

variable "auto_scaling_max_size" {
  type        = number
  description = "Maximum number of App Runner instances during traffic spikes"
  default     = 5
}

variable "auto_scaling_max_concurrency" {
  type        = number
  description = "Max concurrent requests before scaling out a new instance"
  default     = 100
}

variable "image_tag" {
  type        = string
  description = "Docker image tag to deploy"
  default     = "latest"
}
