import click
import command


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument("image")
@click.argument("experiment_id")
@click.option(
    "--run-name",
    "-r",
    metavar="RUN_NAME",
    type=click.STRING,
    help="The name to give the MLflow Run associated with the project execution. If not specified, "
    "the MLflow Run name is left unset.",
)
@click.option(
    "--namespace",
    "-n",
    metavar="NAMESPACE",
    type=click.STRING,
    help="The Kubernetes namespace in which to launch the job.",
)
def fine_tune(
    image: str,
    experiment_id: str,
    run_name: str,
    namespace: str,
) -> None:
    command.fine_tune(
        image=image, experiment_id=experiment_id, run_name=run_name, namespace=namespace
    )


@cli.command()
@click.argument("name")
@click.argument("namespace")
@click.argument("storage_uri")
def deploy(
    name: str,
    namespace: str,
    storage_uri: str,
) -> None:
    command.deploy(name=name, namespace=namespace, storage_uri=storage_uri)


@cli.command()
def destroy(
    name: str,
    namespace: str,
) -> None:
    command.destroy(name=name, namespace=namespace)


if __name__ == "__main__":
    cli()
