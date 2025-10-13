# Define el proveedor de nube (Google Cloud Platform) y la versión requerida.
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

# Configura el proveedor con el proyecto, región y zona que usaremos.
# Estos valores se tomarán de las variables definidas en variables.tf.
provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
  zone    = var.gcp_zone
}