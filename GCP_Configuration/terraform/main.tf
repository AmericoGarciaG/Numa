# main.tf - Orquestador Principal de la Infraestructura de Numa

# Habilitar las APIs de GCP necesarias para nuestro proyecto.
# Terraform se asegurará de que estas APIs estén activas antes de crear los recursos.
resource "google_project_service" "apis" {
  for_each = toset([
    "run.googleapis.com",             # Cloud Run API
    "sqladmin.googleapis.com",        # Cloud SQL Admin API
    "artifactregistry.googleapis.com", # Artifact Registry API
    "iam.googleapis.com",             # IAM API
    "cloudbuild.googleapis.com"       # Cloud Build API (para construir los contenedores)
  ])
  project = var.gcp_project_id
  service = each.key
  disable_on_destroy = false
}