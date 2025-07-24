# Local Development Environment for AWS Glue

This project provides a self-contained, local development environment for AWS Glue jobs using Docker and Docker Compose. It allows you to write, test, and debug your Glue ETL scripts on your local machine without needing to interact with a live AWS environment, saving time and cost.

The setup uses a custom Glue Docker image that is configured to work with a local Hive Metastore, and it leverages LocalStack to emulate AWS S3 for a complete offline experience.

## Features

-   **Run AWS Glue 3.0 Jobs Locally**: Execute your PySpark-based Glue scripts in a containerized environment.
-   **Local Hive Metastore**: Uses a local Hive Metastore for creating databases and tables, mimicking the behavior of the AWS Glue Data Catalog.
-   **S3 Emulation**: Integrates with LocalStack to provide a local S3-compatible object store.
-   **Portable Scripts**: The example script is designed to be portable, running seamlessly in both this local setup and a real AWS Glue environment.
-   **Jupyter Notebook Support**: Includes a Jupyter server within the Glue container for interactive development and debugging.

## How It Works

This environment consists of two main services orchestrated by `docker-compose.yaml`:

1.  **LocalStack**: A container running an emulated S3 service. All S3 operations from the Glue script are directed to this local service.
2.  **Glue Job Runner**: A container built from a custom `Dockerfile` based on the official AWS Glue 3.0 image. The key modification is the removal of the `hive-site.xml` file, which forces Spark to use a local Hive Metastore instead of the AWS Glue Data Catalog.

The two containers are connected on a shared Docker network, allowing the Glue job to communicate with the LocalStack S3 service.

## Getting Started

### Prerequisites

-   [Docker](https://www.docker.com/get-started)
-   [Docker Compose](https://docs.docker.com/compose/install/)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/wj-su/glue-local-runner.git
    cd glue-local-runner
    ```

2.  **Organize your files:**

    Create the following directory structure and place your files accordingly:

    ```
    .
    ├── docker-compose.yaml
    └── glue/
        ├── Dockerfile
        ├── scripts/
        │   └── your_glue_script.py
        └── jupyter_workspace/
    ```

3.  **Build and start the services:**

    Run the following command from the root of the project directory:

    ```bash
    docker-compose up --build
    ```

    This will build the custom Glue image and start both the `localstack` and `glue-job-runner` containers.

## Usage

### Running a Glue Script

To execute your Glue script, you can `exec` into the running `glue-job-runner` container:

1.  **Open a new terminal window.**

2.  **Find the container ID:**

    ```bash
    docker ps
    ```

3.  **Exec into the container:**

    ```bash
    docker exec -it <container_id_or_name> /bin/bash
    ```

4.  **Run the `glue_spark_submit.sh` script:**

    Inside the container, run your script using the provided submission script:

    ```bash
    /home/glue_user/spark/bin/spark-submit --py-files /home/glue_user/aws-glue-libs/glue-python-libs-3.0.0.zip /home/glue_user/scripts/your_glue_script.py --JOB_NAME local_test_job --region us-east-1
    ```

    You should see the output of your script in the console, including the Spark logs and the final DataFrame.

### Using Jupyter Notebook

1.  **Access the Jupyter server:**

    Open your web browser and navigate to `http://localhost:8888`.

2.  **Create and run notebooks:**

    You can now create and run notebooks in the `jupyter_workspace` directory.

## Project Structure

```
├── docker-compose.yaml       # Defines and configures the services.
├── s3-data/                  # (Created automatically) Stores persisted S3 data from LocalStack.
└── glue/
├── Dockerfile            # Builds the custom Glue image.
├── scripts/
│   └── your_glue_script.py # Your Glue ETL script(s).
└── jupyter_workspace/      # For your Jupyter notebooks.
```

## Customization

-   **Adding More Scripts**: Place additional Python scripts in the `./glue/scripts/` directory. They will be automatically mounted into the container.
-   **Changing Glue Version**: To use a different version of Glue, update the `FROM` instruction in the `Dockerfile` to point to the desired `amazon/aws-glue-libs` image tag. You may also need to adjust the path for the `rm /home/glue_user/spark/conf/hive-site.xml` command.
-   **Enabling More AWS Services**: To use other emulated AWS services, add them to the `SERVICES` environment variable in the `localstack` service definition in `docker-compose.yaml`.

## Acknowledgements

The core technique of removing `hive-site.xml` to force a local Hive Metastore was inspired by the solution found in this Stack Overflow thread:

-   [Stack Overflow: Write to local Hive metastore instead of AWS Glue Data Catalog](https://stackoverflow.com/questions/74550609/write-to-local-hive-metastore-instead-of-aws-glue-data-catalog-when-developing-a)