# Guía de Despliegue de Infraestructura de Numa en GCP

Este directorio contiene toda la configuración de Terraform para crear la infraestructura de Numa en Google Cloud Platform.

## Prerrequisitos

1.  **Tener una cuenta de GCP** y un proyecto creado.
2.  **Instalar Terraform:** [Guía oficial de instalación](https://learn.hashicorp.com/tutorials/terraform/install-cli).
3.  **Instalar la CLI de GCP (`gcloud`):** [Guía oficial de instalación](https://cloud.google.com/sdk/docs/install).

## Pasos para el Despliegue

### 1. Autenticación

Primero, necesitas autenticar tu máquina local con GCP. Ejecuta los siguientes comandos en tu terminal:

```bash
gcloud auth login
gcloud auth application-default login
```

Sigue las instrucciones en el navegador para completar el inicio de sesión.

### 2. Configurar el Proyecto

Configura la CLI de gcloud para que apunte a tu proyecto de GCP. Reemplaza `[TU_PROJECT_ID]` con el ID de tu proyecto.

```bash
gcloud config set project [TU_PROJECT_ID]
```

### 3. Preparar las Variables de Terraform

1.  Navega al directorio de Terraform: `cd GCP_Configuration/terraform`
2.  Crea un archivo llamado `terraform.tfvars`. Este archivo contendrá los valores secretos y de configuración. **¡No subas este archivo a Git!**
3.  Añade el siguiente contenido, reemplazando los valores:

    ```tfvars
    gcp_project_id = "[TU_PROJECT_ID]"
    db_password    = "[UNA_CONTRASENA_MUY_SEGURA_PARA_LA_BD]"
    ```

### 4. Inicializar y Aplicar Terraform

1.  **Inicializar Terraform:** Este comando descarga el proveedor de Google Cloud.
    ```bash
    terraform init
    ```

2.  **Planificar los Cambios:** Terraform te mostrará un plan de todos los recursos que va a crear. Revisa que todo sea correcto.
    ```bash
    terraform plan
    ```

3.  **Aplicar los Cambios:** Si el plan es correcto, aplica los cambios para crear la infraestructura en GCP.
    ```bash
    terraform apply
    ```
    Terraform te pedirá una confirmación final. Escribe `yes` y presiona Enter.

¡Listo! Después de unos minutos, tu infraestructura base en GCP estará creada y lista para recibir los contenedores.