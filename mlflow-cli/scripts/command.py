from kubernetes import client, config
import yaml
from typing import Any
from mlflow import tracking
from mlflow.entities.run import Run
from mlflow.projects.kubernetes import KubernetesSubmittedRun
from mlflow.utils.mlflow_tags import (
    MLFLOW_DOCKER_IMAGE_ID,
    MLFLOW_PROJECT_BACKEND,
    MLFLOW_PROJECT_ENV,
    MLFLOW_RUN_NAME,
)
from mlflow.environment_variables import (
    MLFLOW_EXPERIMENT_ID,
    MLFLOW_RUN_ID,
    MLFLOW_TRACKING_URI,
    _EnvironmentVariable,
)

config.load_kube_config()
KUBE_MLFLOW_TRACKING_URI = _EnvironmentVariable("KUBE_MLFLOW_TRACKING_URI", str, None)
AWS_ACCESS_KEY_ID = _EnvironmentVariable("AWS_ACCESS_KEY_ID", str, None)
AWS_SECRET_ACCESS_KEY = _EnvironmentVariable("AWS_SECRET_ACCESS_KEY", str, None)


def fine_tune(
    image: str,
    experiment_id: str,
    run_name: str,
    namespace: str = "mlflow",
) -> KubernetesSubmittedRun:
    active_run: Run = tracking.MlflowClient().create_run(
        experiment_id=experiment_id,
        run_name=run_name,
        tags={
            MLFLOW_PROJECT_BACKEND: "kubernetes",
            MLFLOW_PROJECT_ENV: "docker",
            MLFLOW_RUN_NAME: run_name,
            MLFLOW_DOCKER_IMAGE_ID: image,
        },
    )
    with open(file="./static/templates/job.yaml") as job_template:
        job_template: Any = yaml.safe_load(stream=job_template)
    job_template["metadata"]["name"] = active_run.info.run_name
    job_template["metadata"]["namespace"] = namespace
    job_template["spec"]["template"]["spec"]["containers"][0]["image"] = image
    job_template["spec"]["template"]["spec"]["containers"][0]["env"] += [
        {"name": MLFLOW_TRACKING_URI.name, "value": KUBE_MLFLOW_TRACKING_URI.get()},
        {"name": MLFLOW_EXPERIMENT_ID.name, "value": active_run.info.experiment_id},
        {"name": MLFLOW_RUN_ID.name, "value": active_run.info.run_id},
    ]
    api_instance = client.BatchV1Api()
    api_instance.create_namespaced_job(
        namespace=job_template["metadata"]["namespace"],
        body=job_template,
        pretty=True,
    )
    return KubernetesSubmittedRun(
        mlflow_run_id=active_run.info.run_id,
        job_name=job_template["metadata"]["name"],
        job_namespace=job_template["metadata"]["namespace"],
    )


def deploy(
    name: str,
    namespace: str,
    storage_uri: str,
) -> None:
    with open(file="./static/templates/job.yaml") as inference_service_template:
        inference_service_template: Any = yaml.safe_load(
            stream=inference_service_template
        )
    inference_service_template["metadata"]["name"] = name
    inference_service_template["metadata"]["namespace"] = namespace
    inference_service_template["spec"]["predictor"]["model"]["storageUri"] = storage_uri
    api_instance = client.CustomObjectsApi()
    api_instance.create_namespaced_custom_object(
        group="serving.kserve.io",
        version="v1beta1",
        namespace=namespace,
        plural="inferenceservices",
        body=inference_service_template,
    )


def destroy(
    name: str,
    namespace: str,
) -> None:
    api_instance = client.CustomObjectsApi()
    api_instance.delete_namespaced_custom_object(
        group="serving.kserve.io",
        version="v1beta1",
        namespace=namespace,
        plural="inferenceservices",
        name=name,
    )
