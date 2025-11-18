# Oncoanalyser Plugin for `nflaunch`

This plugin enables automated generation of a valid **samplesheet** for the [nf-core/oncoanalyser](https://nf-co.re/oncoanalyser) pipeline using paired tumor-normal samples stored in a Google Cloud Storage (GCS) bucket.

It is intended to be used with the `nflaunch` tool and simplifies setup for running **paired DNA analyses** by dynamically fetching BAM/CRAM files and generating a compatible CSV samplesheet.

## Purpose

The nf-core/oncoanalyser pipeline expects a structured `samplesheet.csv` as input. This plugin:

- Accepts a tumor-normal sample ID pair (via `--sample-id`)
- Searches a GCS bucket for matching files (via `--plugin-options`)
- Generates a properly formatted `samplesheet.csv`
- Registers the samplesheet path on the job config, enabling `nflaunch` to use it during job submission

## Usage

In your `nflaunch` command, specify:

```bash
--plugin oncoanalyser \
--plugin-options '{"remote_sample_bucket_uri": "gs://your-bucket/path", "filetype": "bam"}' \
--sample-id TUMOR123,NORMAL456
```

## Plugin Options

| Option                     | Description                                                          |
| -------------------------- | -------------------------------------------------------------------- |
| `remote_sample_bucket_uri` | GCS URI where sample files are located (e.g., `gs://my-bucket/data`) |
| `filetype`                 | Extension of the input files (`bam` or `cram`)                       |

### Example

```bash
nflaunch \
  --pipeline-name nf-core/oncoanalyser \
  --pipeline-version 2.1.0 \
  --params-file params.yaml \
  --sample-id TUMOR123,NORMAL456 \
  ...
  --plugin oncoanalyser \
  --plugin-options '{"remote_sample_bucket_uri": "gs://my-bucket/samples", "filetype": "bam"}'
```

This will:

1. Locate the latest BAM files for `TUMOR123` and `NORMAL456` in the GCS bucket.
2. Write a samplesheet to `.tmp/<workflowrun_id>/samplesheet.csv` with the following structure:

```csv
group_id,subject_id,sample_id,sample_type,sequence_type,filetype,filepath
TUMOR123_NORMAL456,TUMOR123_NORMAL456,TUMOR123,tumor,dna,bam,gs://.../TUMOR123.bam
TUMOR123_NORMAL456,TUMOR123_NORMAL456,TUMOR123,tumor,dna,bai,gs://.../TUMOR123.bam.bai
TUMOR123_NORMAL456,TUMOR123_NORMAL456,NORMAL456,normal,dna,bam,gs://.../NORMAL456.bam
TUMOR123_NORMAL456,TUMOR123_NORMAL456,NORMAL456,normal,dna,bai,gs://.../NORMAL456.bam.bai
```

3. Use the generated file during pipeline execution via the `--samplesheet` parameter.

## Requirements

* The input files (`bam` or `cram`) and their index files (`.bai` or `.crai`) must be present in the specified GCS path.
* `--sample-id` must be in the format: `TUMOR_ID,NORMAL_ID`
* Plugin must be enabled with `--plugin oncoanalyser`

## Output

* A CSV file at `.tmp/<workflowrun_id>/samplesheet.csv`
* Log messages indicating the samplesheet location and file references

## Notes

* In **dry-run mode**, the plugin logs the intended samplesheet path but does not generate the file.
* This plugin assumes GCS bucket access is properly configured and authenticated using the service account provided to `nflaunch`.
