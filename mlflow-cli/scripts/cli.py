import click
import command


@click.group(
    help="""
    This CLI provides a set of commands to interact with MLflow in a Kubernetes cluster.
    """
)
def cli() -> None:
    pass


@cli.command(
    help="""
    This command runs a job with the given parameters.

    Arguments:
        image         The Docker image to use for the job.
        experiment_id The experiment ID associated with this run.
        run_name      The name to give the MLflow Run. Optional.

    Options:
        --namespace, -n  The Kubernetes namespace in which to launch the job.
        --dry-run, -d    If set, the job will not be submitted to the Kubernetes cluster.

    Example:
        mlflow-cli run gcr.io/your-project/your-image 430758536676277373 fine-tune -n mlflow
    """
)
@click.argument("image")
@click.argument("experiment_id")
@click.argument("run_name")
@click.option(
    "--namespace",
    "-n",
    metavar="NAMESPACE",
    default="mlflow",
    type=click.STRING,
    help="The Kubernetes namespace in which to launch the job.",
)
@click.option(
    "--dry-run",
    "-d",
    default=False,
    is_flag=True,
    help="If set, the job will not be submitted to the Kubernetes cluster.",
)
def fine_tune(
    image: str,
    experiment_id: str,
    run_name: str,
    namespace: str,
    dry_run: bool,
) -> None:
    command.fine_tune(
        image=image,
        experiment_id=experiment_id,
        run_name=run_name,
        namespace=namespace,
        dry_run=dry_run,
    )


@cli.command(
    help="""
    This command kills a job with the given parameters.

    Arguments:
        run_id    The ID of the run to kill.

    Example:
        mlflow-cli kill c3dce6c6bcc245c2b7dd37924bb958e0
    """
)
@click.argument("run_id")
def kill(
    run_id: str,
) -> None:
    command.kill(run_id=run_id)


@cli.command(
    help="""
    This command deploys a inference service with the given parameters.

    Arguments:
        name          The name of the deployment.
        experiment_id The experiment ID associated with this run.
        run_id        The run ID associated with this run.
        model_name    The name of the model to deploy.

    Options:
        --namespace, -n  The Kubernetes namespace in which to launch the job.
        --storage_uri, -s  The storage URI to use for the model.

    Example:
        mlflow-cli deploy 430758536676277373 c3dce6c6bcc245c2b7dd37924bb958e0 multilingual-e5-large -n mlflow -s mlflow
    """
)
@click.argument("name")
@click.argument("experiment_id")
@click.argument("run_id")
@click.argument("model_name")
@click.option(
    "--namespace",
    "-n",
    metavar="NAMESPACE",
    default="mlflow",
    type=click.STRING,
    help="The Kubernetes namespace in which to launch the job.",
)
@click.option(
    "--storage_uri",
    "-s",
    metavar="STORAGE_URI",
    default="mlflow",
    type=click.STRING,
    help="The storage URI to use for the model.",
)
@click.option(
    "--dry-run",
    "-d",
    default=False,
    is_flag=True,
    help="If set, the job will not be submitted to the Kubernetes cluster.",
)
def deploy(
    name: str,
    experiment_id: str,
    run_id: str,
    model_name: str,
    namespace: str,
    storage_uri: str,
    dry_run: bool,
) -> None:
    command.deploy(
        name=name,
        experiment_id=experiment_id,
        run_id=run_id,
        model_name=model_name,
        namespace=namespace,
        storage_uri=storage_uri,
        dry_run=dry_run,
    )


@cli.command(
    help="""
    This command destroys a deployment with the given parameters.

    Arguments:
        name      The name of the deployment.
        namespace The Kubernetes namespace in which deployment is running.

    Example:
        mlflow-cli destroy multilingual-e5-large mlflow
    """
)
@click.argument("name")
@click.argument("namespace")
def destroy(
    name: str,
    namespace: str,
) -> None:
    command.destroy(name=name, namespace=namespace)


if __name__ == "__main__":
    cli()
