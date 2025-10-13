# Variables de configuración del proyecto en GCP
variable "gcp_project_id" {
  description = "El ID del proyecto de GCP donde se desplegará la infraestructura."
  type        = string
}

variable "gcp_region" {
  description = "La región principal para los recursos de GCP."
  type        = string
  default     = "us-central1"
}

variable "gcp_zone" {
  description = "La zona principal para los recursos de GCP."
  type        = string
  default     = "us-central1-a"
}

variable "db_password" {
  description = "La contraseña para el usuario principal de la base de datos Cloud SQL."
  type        = string
  sensitive   = true # Marca la variable como sensible para que no se muestre en los logs.
}