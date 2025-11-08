---
title: Common S3 CLI Commands
created: 2025-10-18T00:00:00Z
updated: 2025-10-18T00:00:00Z
tags: [s3, aws-cli-s3]
---

## Create a bucket

```
aws s3api create-bucket --bucket my-example-bucket-ab --region us-east-1
```
## Listing all buckets

```
aws s3api list-buckets --query "Buckets[].Name"
```
## Uploading objects

### Single object

```
aws s3 cp path/to/local/file.txt s3://my-example-bucket-ab/
```

### Multiple objects using sync

```
aws s3 sync path/to/local/directory/ s3://my-example-bucket-ab/
```
## Downloading objects

### Single object

```
aws s3 cp s3://my-example-bucket-ab/file.txt path/to/local/directory/
```

### Multiple objects using sync

```
aws s3 sync s3://my-example-bucket-ab/ path/to/local/directory/
```
## Listing objects

```
aws s3api list-objects --bucket my-example-bucket-ab --query "Contents[].Key"
```
### Exclude folder names from results
When listing objects, folder names end with a `/`. You can exclude these results by applying a JMESPath query.

```
aws s3api list-objects --bucket my-example-bucket-ab --query 'Contents[?(!ends_with(Key, `/`))].Key'
```
## Deleting objects
### Delete a single object
```
aws s3 rm s3://my-example-bucket-ab/file.txt
```

## Delete all objects recursively

```
aws s3 rm s3://my-example-bucket-ab/ --recursive
```
## Deleting buckets

```
aws s3api delete-bucket --bucket my-example-bucket-ab
```

## Advanced

### Get Object metadata

```
aws s3api head-object --bucket my-example-bucket-ab --key file.txt
```

### Enable Versioning

```
aws s3api put-bucket-versioning --bucket my-example-bucket-ab --versioning-configuration Status=Enabled
```

Links: [[s3]] [[aws cli s3]]