"""Oncoanalyser plugin for generating nf-core/oncoanalyser samplesheets."""

import csv
from pathlib import Path

from nflaunch.backends.gcp.file import get_latest_file, parse_gcs_path
from nflaunch.plugins.base import Plugin


class OncoanalyserPlugin(Plugin):
    """
    Generate nf-core/oncoanalyser samplesheets from paired tumor/normal identifiers.

    The plugin writes a temporary `samplesheet.csv` compatible with
    https://nf-co.re/oncoanalyser/2.1.0/docs/usage/#paired-tumor-and-normal-dna by retrieving the
    latest BAM/CRAM assets from a remote GCS bucket. The bucket location and file extensions are
    provided via `--plugin-options`, while tumor/normal IDs arrive via `--sample-id`.
    """

    def load(self) -> None:
        """
        Prepare plugin resources and update the job configuration.
        """
        self._build_samplesheet()

    def _build_samplesheet(self) -> None:
        """
        Create a samplesheet CSV file based on tumor/normal sample pairs.

        The CSV is written to `.tmp/<workflowrun_id>/samplesheet.csv`, recorded on the job config,
        and includes both data files and index files for each sample.
        """
        job_config = self.job_config
        tmp_dir = Path(job_config.tmp_dir)
        tmp_csv = tmp_dir / "samplesheet.csv"
        job_config.samplesheet = str(tmp_csv)

        if job_config.dry_run:
            self.logger.info(f"[DRY-RUN] samplesheet will be written to: {tmp_csv}")

        plugin_options = dict(job_config.plugin_options)
        bucket_uri = plugin_options.get("remote_sample_bucket_uri")
        if bucket_uri is None:
            raise ValueError(
                "Oncoanalyser plugin requires 'remote_sample_bucket_uri' in plugin options."
            )
        filename_extension = plugin_options.get("filetype")
        if filename_extension is None:
            raise ValueError("Oncoanalyser plugin requires 'filetype' in plugin options.")

        sample_id = job_config.sample_id
        if not sample_id or "," not in sample_id:
            raise ValueError(
                "Oncoanalyser plugin expects --sample-id in 'TUMOR_ID,NORMAL_ID' format."
            )

        bucket_name, bucket_prefix = parse_gcs_path(bucket_uri)

        tumor_id, normal_id = (part.strip() for part in sample_id.split(",", maxsplit=1))

        tumor_bam = get_latest_file(
            bucket_name=bucket_name,
            bucket_prefix=bucket_prefix,
            filename_prefix=tumor_id,
            filename_extension=filename_extension,
        )
        normal_bam = get_latest_file(
            bucket_name=bucket_name,
            bucket_prefix=bucket_prefix,
            filename_prefix=normal_id,
            filename_extension=filename_extension,
        )

        entries = [
            {
                "sequence_type": "dna",
                "sample_id": tumor_id,
                "sample_type": "tumor",
                "filetype": "bam",
                "filepath": tumor_bam,
            },
            {
                "sequence_type": "dna",
                "sample_id": tumor_id,
                "sample_type": "tumor",
                "filetype": "bai",
                "filepath": tumor_bam + ".bai",
            },
            {
                "sequence_type": "dna",
                "sample_id": normal_id,
                "sample_type": "normal",
                "filetype": "bam",
                "filepath": normal_bam,
            },
            {
                "sequence_type": "dna",
                "sample_id": normal_id,
                "sample_type": "normal",
                "filetype": "bai",
                "filepath": normal_bam + ".bai",
            },
        ]

        tmp_dir.mkdir(parents=True, exist_ok=True)

        with open(tmp_csv, mode="w", newline="") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "group_id",
                    "subject_id",
                    "sample_id",
                    "sample_type",
                    "sequence_type",
                    "filetype",
                    "filepath",
                ],
            )
            writer.writeheader()
            for row in entries:
                row["group_id"] = f"{tumor_id}_{normal_id}"
                row["subject_id"] = f"{tumor_id}_{normal_id}"
                writer.writerow(row)

        self.logger.info(f"Samplesheet written to {tmp_csv}")
