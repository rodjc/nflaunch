"""Command-line argument parser for nflaunch."""

import argparse
import sys
from importlib.metadata import version

from nflaunch.cli.formatter import CustomHelpFormatter
from nflaunch.cli.validator import Validator

VERSION = version("nflaunch")


def parse_args() -> argparse.Namespace:
    """
    Parse CLI arguments and return an argparse namespace.
    """
    parser = argparse.ArgumentParser(
        prog="nflaunch",
        usage="%(prog)s OPTIONS",
        description="Run your Nextflow pipelines in the cloud, effortlessly",
        formatter_class=CustomHelpFormatter,
        add_help=False,
        allow_abbrev=False,
    )

    # General options
    general = parser.add_argument_group("General options")

    general.add_argument("-h", "--help", action="help", help="Show this help message and exit.")
    general.add_argument(
        "--version",
        action="version",
        version=f"nflaunch {VERSION}",
        help="Show program version and exit.",
    )
    general.add_argument(
        "-b",
        "--base-bucket",
        required=True,
        type=Validator.bucket_name,
        help=(
            "Cloud storage bucket used for configs, logs, cache, and work directories "
            "(e.g., gs://my-bucket or my-bucket)."
        ),
        metavar="",
    )
    general.add_argument(
        "-i",
        "--container-image",
        default="nextflow/nextflow",
        help="Docker image that contains Nextflow and any required dependencies.",
        metavar="",
    )
    general.add_argument(
        "-s",
        "--sample-id",
        help="Identifier for the input sample(s) to be processed.",
        metavar="",
    )
    general.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Print job configuration without submitting it to the cloud backend.",
    )
    general.add_argument(
        "-e",
        "--backend",
        type=Validator.backend_aliases,
        default="google-batch",
        help=(
            "Batch processing backend to use. Currently only 'google-batch' is supported "
            "(alias: 'gcp-batch')."
        ),
        metavar="",
    )
    general.add_argument(
        "-c",
        "--remote-cache-path",
        default=None,
        help=(
            "Remote GCS path for the Nextflow cache directory. Defaults to 'BASE_BUCKET/cache' "
            "when omitted."
        ),
        metavar="",
    )
    general.add_argument(
        "-r",
        "--remote-run-path",
        default=None,
        help=(
            "Remote GCS path where config files and Nextflow report/trace/timeline are stored. "
            "Defaults to 'BASE_BUCKET/run' when omitted."
        ),
        metavar="",
    )

    # GCP Batch options
    google_batch = parser.add_argument_group("GCP Batch options")
    google_batch.add_argument(
        "--project-id", required=True, help="Google Cloud project ID.", metavar=""
    )
    google_batch.add_argument(
        "--region",
        required=True,
        help="Google Cloud region in which to run the Batch job.",
        metavar="",
    )
    google_batch.add_argument(
        "--service-account-email",
        required=True,
        type=Validator.sa_email,
        help=(
            "Service account email with permissions to launch Batch jobs and access "
            "Google Cloud Storage."
        ),
        metavar="",
    )
    google_batch.add_argument(
        "--network",
        required=True,
        help="VPC network name to attach to the VM (required for shared VPCs).",
        metavar="",
    )
    google_batch.add_argument(
        "--subnetwork",
        required=True,
        help="Subnetwork name to attach to the VM (required for shared VPCs).",
        metavar="",
    )
    google_batch.add_argument(
        "--spot",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Use Spot instances. Use --no-spot to disable.",
    )
    google_batch.add_argument(
        "--labels",
        type=Validator.json_obj,
        default=None,
        help=("JSON object of labels for the Nextflow runner " '(e.g., \'{"team":"oncology"}\').'),
        metavar="",
    )
    google_batch.add_argument(
        "--upload-max-workers",
        type=int,
        default=0,
        help=(
            "Max parallel workers for uploading pipeline directories to GCS. Use 0 for "
            "automatic CPU-count detection."
        ),
        metavar="",
    )
    google_batch.add_argument(
        "--cpu-milli",
        type=Validator.positive_int,
        default=None,
        help="Requested CPU for the Batch task in millicores (e.g., 4000 for 4 vCPU).",
        metavar="",
    )
    google_batch.add_argument(
        "--memory-mib",
        type=Validator.positive_int,
        default=None,
        help="Requested memory for the Batch task in MiB (e.g., 8192 for 8 GiB).",
        metavar="",
    )
    google_batch.add_argument(
        "--machine-type",
        default=None,
        help=(
            "Machine type for Batch worker VMs (e.g., e2-standard-4). Defaults to the "
            "provider recommended type."
        ),
        metavar="",
    )

    # Nextflow Pipeline options
    nextflow = parser.add_argument_group("Nextflow options")
    nextflow.add_argument(
        "--pipeline-name",
        required=True,
        help=(
            "Pipeline name (GitHub-style like 'nf-core/rnaseq'), local folder path "
            "(e.g., '/path/to/pipeline'), or '.' for the current directory."
        ),
        metavar="",
    )
    nextflow.add_argument(
        "--nextflow-version",
        default="25.04.6",
        help="Version of Nextflow to use (e.g., 25.04.6).",
        metavar="",
    )
    nextflow.add_argument(
        "--pipeline-version", help="Specific version/tag of the pipeline to run.", metavar=""
    )
    nextflow.add_argument(
        "--profile", help="Profile defined in the Nextflow config file.", metavar=""
    )
    nextflow.add_argument(
        "--params-file",
        type=Validator.existing_path,
        help="Path to a YAML/JSON file containing pipeline parameters.",
        metavar="",
    )
    nextflow.add_argument(
        "--config-file",
        type=Validator.existing_path,
        help="Path to a custom Nextflow configuration file.",
        metavar="",
    )
    nextflow.add_argument(
        "--executor-config-file",
        type=Validator.existing_path,
        help="Path to the Nextflow cloud executor configuration file.",
        metavar="",
    )
    nextflow.add_argument(
        "--samplesheet",
        type=Validator.existing_path,
        help="Path to the input CSV samplesheet used by the pipeline.",
        metavar="",
    )
    nextflow.add_argument(
        "--resume",
        help="Resume a previous pipeline execution. Format: WORKFLOWRUN_ID,WORKFLOW_SESSION.",
        metavar="",
    )

    # Plugin options
    plugin = parser.add_argument_group("Plugin options")
    plugin.add_argument(
        "-p",
        "--plugin",
        default=None,
        help="Plugin name to be added to the backend options.",
        metavar="",
    )
    plugin.add_argument(
        "-o",
        "--plugin-options",
        type=Validator.json_obj,
        default=None,
        help=(
            "JSON object of plugin options for the selected plugin "
            '(e.g., \'{"sample_group": "clinical"}\').'
        ),
        metavar="",
    )

    if len(sys.argv) == 1:
        parser.print_help()
        parser.exit()

    return parser.parse_args()
