import logging

logging.basicConfig(level=logging.DEBUG)

from typing import Any

import yaml
from kubernetes import client, config
from mlflow import tracking
from mlflow.entities.run import Run, RunInfo
from mlflow.environment_variables import (
    MLFLOW_EXPERIMENT_ID,
    MLFLOW_RUN_ID,
    MLFLOW_TRACKING_URI,
    _EnvironmentVariable,
)
from mlflow.projects.kubernetes import KubernetesSubmittedRun
from mlflow.utils.mlflow_tags import (
    MLFLOW_DOCKER_IMAGE_ID,
    MLFLOW_PROJECT_BACKEND,
    MLFLOW_PROJECT_ENV,
    MLFLOW_RUN_NAME,
)

config.load_kube_config()
KUBE_MLFLOW_TRACKING_URI = _EnvironmentVariable("KUBE_MLFLOW_TRACKING_URI", str, None)
AWS_ACCESS_KEY_ID = _EnvironmentVariable("AWS_ACCESS_KEY_ID", str, None)
AWS_SECRET_ACCESS_KEY = _EnvironmentVariable("AWS_SECRET_ACCESS_KEY", str, None)


def fine_tune(
    image: str,
    experiment_id: str,
    run_name: str,
    namespace: str,
    dry_run: bool = False,
) -> KubernetesSubmittedRun:
    """
    Run a job on Kubernetes.

    Args:
        image (str): Container image to run the job.
        experiment_id (str): mlflow experiment id.
        run_name (str): mlflow run name.
        namespace (str, optional): Kubernetes namespace to run the job.

    Returns:
        KubernetesSubmittedRun: _description_
    """

    active_run: Run = (
        tracking.MlflowClient().create_run(
            experiment_id=experiment_id,
            run_name=run_name,
            tags={
                MLFLOW_PROJECT_BACKEND: "kubernetes",
                MLFLOW_PROJECT_ENV: "docker",
                MLFLOW_RUN_NAME: run_name,
                MLFLOW_DOCKER_IMAGE_ID: image,
            },
        )
        if not dry_run
        else Run(
            run_data=None,
            run_info=RunInfo(
                run_uuid="run_uuid",
                user_id="user_id",
                status="status",
                start_time="start_time",
                end_time="end_time",
                lifecycle_stage="lifecycle_stage",
                experiment_id=experiment_id,
                run_name=run_name,
                run_id="dry_run",
            ),
        )
    )

    with open(file="./static/templates/job.yaml") as template:
        manifest: Any = yaml.safe_load(stream=template)
    manifest["metadata"]["name"] = active_run.info.run_name
    manifest["metadata"]["namespace"] = namespace
    manifest["spec"]["template"]["spec"]["containers"][0]["image"] = image
    manifest["spec"]["template"]["spec"]["containers"][0]["env"] += [
        {"name": MLFLOW_TRACKING_URI.name, "value": KUBE_MLFLOW_TRACKING_URI.get()},
        {"name": MLFLOW_EXPERIMENT_ID.name, "value": active_run.info.experiment_id},
        {"name": MLFLOW_RUN_ID.name, "value": active_run.info.run_id},
    ]
    logging.info(f"Creating job {active_run.info.run_name} in namespace {namespace}")
    api_instance = client.BatchV1Api()
    api_instance.create_namespaced_job(
        namespace=manifest["metadata"]["namespace"],
        body=manifest,
        pretty=True,
        dry_run="All" if dry_run else None,
    )
    return KubernetesSubmittedRun(
        mlflow_run_id=active_run.info.run_id,
        job_name=manifest["metadata"]["name"],
        job_namespace=manifest["metadata"]["namespace"],
    )


def deploy(
    name: str,
    experiment_id: str,
    run_id: str,
    model_name: str,
    namespace: str,
    storage_uri: str,
    dry_run: bool = False,
) -> None:
    """
    Deploy a model as a kserve inference service.

    Args:
        name (str): name of the inference service.
        experiment_id (str): mlflow experiment id.
        run_id (str): mlflow run id.
        model_name (str): mlflow model name.
        namespace (str): Kubernetes namespace to deploy the service.
        storage_uri (str): S3 URI to the model artifacts.
    """
    with open(file="./static/templates/inference_service.yaml", mode="r") as template:
        manifest: Any = yaml.safe_load(stream=template)
    manifest["metadata"]["name"] = name
    manifest["metadata"]["namespace"] = namespace

    for env_var in manifest["spec"]["predictor"]["containers"][0]["env"]:
        if env_var["name"] == "STORAGE_URI":
            env_var["value"] = (
                f"s3://{storage_uri}/{experiment_id}/{run_id}/artifacts/{model_name}"
            )
        if env_var["name"] == "APP_ARGS":
            env_var["value"] = f"--model_name {model_name} --predictor_protocol v2"

    api_instance = client.CustomObjectsApi()
    api_instance.create_namespaced_custom_object(
        group="serving.kserve.io",
        version="v1beta1",
        namespace=namespace,
        plural="inferenceservices",
        body=manifest,
        dry_run="All" if dry_run else None,
    )


def destroy(
    name: str,
    namespace: str = "mlflow",
) -> None:
    """
    Destroy a kserve inference service.

    Args:
        name (str): name of the inference service.
        namespace (str): Kubernetes namespace to destroy the service.
    """
    api_instance = client.CustomObjectsApi()
    api_instance.delete_namespaced_custom_object(
        group="serving.kserve.io",
        version="v1beta1",
        namespace=namespace,
        plural="inferenceservices",
        name=name,
    )
