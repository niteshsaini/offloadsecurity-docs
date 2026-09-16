#!/usr/bin/env python3
"""Seed a coherent Cloud Security dataset for documentation screenshots.

Owns everything for TEAM in: enhanced_cloud_accounts (prunes to 4 accounts),
cspm_orchestration.scan_runs, cspm_cloud_security.findings / compliance_scores /
remediation_tasks, cspm_cloud_assets.assets, cspm_platform.cloud_events.

Deterministic (seeded RNG); timestamps are relative to now so re-runs stay fresh.
Shapes mirror the writers: models/scan_orchestration_models.ScanRun,
services/cspm_prowler_ingestor._normalize_finding + compliance_scores writer,
routes/cspm_findings_routes remediation task doc, cloud_event_ingestion_service.
"""
import os, random, uuid, hashlib, sys
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient

TEAM = "default-team"
USER = "b54cf4e7-3434-4ab4-aa74-632f23b92a2b"
KEEP = {"478915623094", "613920475168", "offload-prod-platform-481523",
        "7e3a9c14-2f6b-4d80-bb15-9a4e2c1f7d63"}
NOW = datetime.now(timezone.utc).replace(microsecond=0)
rng = random.Random(20260911)

def ago(days=0, hours=0, minutes=0):
    return NOW - timedelta(days=days, hours=hours, minutes=minutes)

def hid(*parts, n=16):
    return hashlib.sha1("|".join(map(str, parts)).encode()).hexdigest()[:n]

SEV_SCORE = {"critical": 10.0, "high": 7.5, "medium": 5.0, "low": 2.5, "informational": 1.0}
SEV_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3, "informational": 4}

# ---------------------------------------------------------------- check catalog
# (check_id, title, severity, service, resource_type, category, frameworks, remediation text, url)
AWS = [
 ("s3_bucket_public_access","S3 bucket has public access enabled","critical","s3","AwsS3Bucket","storage",
  {"cis_3_0_aws":["2.1.5"],"nist_800_53_revision_5":["AC-3","SC-7"],"pci_dss_v4_0":["1.3.1"],"aws_foundational_security":["S3.2"],"soc2":["CC6.1"]},
  "Enable S3 Block Public Access at the bucket (and account) level and remove public bucket policies/ACLs.","https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html"),
 ("s3_bucket_default_encryption","S3 bucket does not have default encryption enabled","medium","s3","AwsS3Bucket","encryption",
  {"cis_3_0_aws":["2.1.1"],"nist_800_53_revision_5":["SC-28"],"pci_dss_v4_0":["3.5.1"],"iso27001_2022_aws":["A.8.24"]},
  "Enable default encryption (SSE-S3 or SSE-KMS) on the bucket.","https://docs.aws.amazon.com/AmazonS3/latest/userguide/default-bucket-encryption.html"),
 ("s3_bucket_server_access_logging_enabled","S3 bucket server access logging is disabled","medium","s3","AwsS3Bucket","logging",
  {"cis_3_0_aws":["3.6"],"nist_800_53_revision_5":["AU-2"],"soc2":["CC7.2"]},
  "Enable server access logging and deliver logs to a dedicated, locked-down logging bucket.","https://docs.aws.amazon.com/AmazonS3/latest/userguide/ServerLogs.html"),
 ("iam_root_mfa_enabled","Root account does not have MFA enabled","critical","iam","AwsIamUser","iam",
  {"cis_3_0_aws":["1.5"],"nist_800_53_revision_5":["IA-2(1)"],"pci_dss_v4_0":["8.4.2"],"aws_foundational_security":["IAM.9"],"soc2":["CC6.1"]},
  "Enable a hardware MFA device on the root user and lock the credentials away.","https://docs.aws.amazon.com/IAM/latest/UserGuide/id_root-user.html#id_root-user_manage_mfa"),
 ("iam_user_mfa_enabled_console_access","IAM user with console access has no MFA","high","iam","AwsIamUser","iam",
  {"cis_3_0_aws":["1.10"],"nist_800_53_revision_5":["IA-2(1)"],"pci_dss_v4_0":["8.4.2"],"aws_foundational_security":["IAM.5"]},
  "Require MFA for all console users via an IAM policy condition and enrol the users.","https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_mfa.html"),
 ("iam_rotate_access_key_90_days","IAM access key older than 90 days","medium","iam","AwsIamAccessKey","iam",
  {"cis_3_0_aws":["1.14"],"nist_800_53_revision_5":["IA-5(1)"],"pci_dss_v4_0":["8.3.9"]},
  "Rotate the access key and delete the old one; prefer roles over long-lived keys.","https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_RotateAccessKey"),
 ("iam_user_accesskey_unused","IAM access key unused for more than 45 days","medium","iam","AwsIamAccessKey","iam",
  {"cis_3_0_aws":["1.12"],"aws_foundational_security":["IAM.8"]},
  "Deactivate and delete unused access keys.","https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#remove-credentials"),
 ("iam_policy_attached_only_to_group_or_roles","IAM policy attached directly to a user","low","iam","AwsIamUser","iam",
  {"cis_3_0_aws":["1.15"],"nist_800_53_revision_5":["AC-6"]},
  "Attach policies to groups or roles and add the user to the group.","https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#use-groups-for-permissions"),
 ("ec2_securitygroup_allow_ingress_from_internet_to_any_port","Security group allows ingress from 0.0.0.0/0 to any port","high","ec2","AwsEc2SecurityGroup","network",
  {"cis_3_0_aws":["5.2"],"nist_800_53_revision_5":["SC-7"],"pci_dss_v4_0":["1.3.1"],"aws_foundational_security":["EC2.18"]},
  "Restrict the inbound rule to specific ports and trusted CIDR ranges.","https://docs.aws.amazon.com/vpc/latest/userguide/security-group-rules.html"),
 ("ec2_securitygroup_allow_ingress_from_internet_to_tcp_port_22","Security group allows SSH (22) from the internet","high","ec2","AwsEc2SecurityGroup","network",
  {"cis_3_0_aws":["5.2"],"nist_800_53_revision_5":["SC-7"],"pci_dss_v4_0":["1.3.1"],"aws_foundational_security":["EC2.13"]},
  "Remove the 0.0.0.0/0 rule for port 22; use SSM Session Manager or a bastion with restricted CIDRs.","https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html"),
 ("ec2_ebs_volume_encryption","EBS volume is not encrypted","medium","ec2","AwsEc2Volume","encryption",
  {"cis_3_0_aws":["2.2.1"],"nist_800_53_revision_5":["SC-28"],"pci_dss_v4_0":["3.5.1"],"aws_foundational_security":["EC2.3"]},
  "Snapshot, copy with encryption, and replace the volume; enable EBS encryption by default for the region.","https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSEncryption.html"),
 ("ec2_instance_public_ip","EC2 instance has a public IP address","medium","ec2","AwsEc2Instance","network",
  {"nist_800_53_revision_5":["SC-7"],"aws_foundational_security":["EC2.9"]},
  "Move the instance to a private subnet behind a load balancer or NAT gateway.","https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Scenario2.html"),
 ("ec2_imdsv2_enabled","EC2 instance allows IMDSv1","medium","ec2","AwsEc2Instance","compute",
  {"nist_800_53_revision_5":["AC-3"],"aws_foundational_security":["EC2.8"]},
  "Set HttpTokens=required on the instance metadata options.","https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html"),
 ("rds_instance_no_public_access","RDS instance is publicly accessible","critical","rds","AwsRdsDbInstance","network",
  {"cis_3_0_aws":["2.3.3"],"nist_800_53_revision_5":["SC-7"],"pci_dss_v4_0":["1.3.1"],"aws_foundational_security":["RDS.2"],"soc2":["CC6.6"]},
  "Set PubliclyAccessible=false and place the instance in private subnets.","https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_VPC.WorkingWithRDSInstanceinaVPC.html"),
 ("rds_instance_storage_encrypted","RDS instance storage is not encrypted","high","rds","AwsRdsDbInstance","encryption",
  {"cis_3_0_aws":["2.3.1"],"nist_800_53_revision_5":["SC-28"],"pci_dss_v4_0":["3.5.1"],"aws_foundational_security":["RDS.3"]},
  "Create an encrypted snapshot copy and restore into a new encrypted instance.","https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Overview.Encryption.html"),
 ("rds_instance_backup_enabled","RDS instance has automated backups disabled","medium","rds","AwsRdsDbInstance","compute",
  {"nist_800_53_revision_5":["CP-9"],"aws_foundational_security":["RDS.11"],"soc2":["A1.2"]},
  "Set a backup retention period of at least 7 days.","https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithAutomatedBackups.html"),
 ("cloudtrail_multi_region_enabled","No multi-region CloudTrail trail is enabled","high","cloudtrail","AwsCloudTrailTrail","logging",
  {"cis_3_0_aws":["3.1"],"nist_800_53_revision_5":["AU-2","AU-12"],"pci_dss_v4_0":["10.2.1"],"aws_foundational_security":["CloudTrail.1"],"soc2":["CC7.2"]},
  "Create an organization or multi-region trail with log file validation enabled.","https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-create-and-update-a-trail.html"),
 ("cloudtrail_log_file_validation_enabled","CloudTrail log file validation is disabled","medium","cloudtrail","AwsCloudTrailTrail","logging",
  {"cis_3_0_aws":["3.2"],"nist_800_53_revision_5":["AU-9"],"aws_foundational_security":["CloudTrail.4"]},
  "Enable log file validation on the trail.","https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-enabling.html"),
 ("vpc_flow_logs_enabled","VPC flow logs are disabled","medium","vpc","AwsEc2Vpc","logging",
  {"cis_3_0_aws":["3.7"],"nist_800_53_revision_5":["AU-12"],"pci_dss_v4_0":["10.2.1"],"aws_foundational_security":["EC2.6"]},
  "Enable VPC flow logs to CloudWatch Logs or S3 for the VPC.","https://docs.aws.amazon.com/vpc/latest/userguide/flow-logs.html"),
 ("kms_cmk_rotation_enabled","KMS customer managed key rotation is disabled","medium","kms","AwsKmsKey","encryption",
  {"cis_3_0_aws":["3.6"],"nist_800_53_revision_5":["SC-12"],"pci_dss_v4_0":["3.7.4"],"aws_foundational_security":["KMS.4"]},
  "Enable automatic annual key rotation on the CMK.","https://docs.aws.amazon.com/kms/latest/developerguide/rotate-keys.html"),
 ("lambda_function_url_public","Lambda function URL is publicly accessible","high","lambda","AwsLambdaFunction","network",
  {"nist_800_53_revision_5":["AC-3"],"aws_foundational_security":["Lambda.1"]},
  "Set the function URL auth type to AWS_IAM or front it with API Gateway.","https://docs.aws.amazon.com/lambda/latest/dg/urls-auth.html"),
 ("lambda_function_no_secrets_in_variables","Lambda environment variables contain potential secrets","high","lambda","AwsLambdaFunction","compute",
  {"nist_800_53_revision_5":["IA-5(7)"],"pci_dss_v4_0":["8.6.2"]},
  "Move secrets to Secrets Manager or SSM Parameter Store and reference them at runtime.","https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html#configuration-envvars-encryption"),
 ("eks_endpoints_not_publicly_accessible","EKS cluster API endpoint is public","high","eks","AwsEksCluster","network",
  {"nist_800_53_revision_5":["SC-7"],"aws_foundational_security":["EKS.1"]},
  "Enable private endpoint access and restrict public access CIDRs.","https://docs.aws.amazon.com/eks/latest/userguide/cluster-endpoint.html"),
 ("eks_control_plane_logging_all_types_enabled","EKS control plane logging is not fully enabled","medium","eks","AwsEksCluster","logging",
  {"nist_800_53_revision_5":["AU-2"],"aws_foundational_security":["EKS.8"]},
  "Enable api, audit, authenticator, controllerManager and scheduler logs.","https://docs.aws.amazon.com/eks/latest/userguide/control-plane-logs.html"),
 ("guardduty_is_enabled","GuardDuty is not enabled in the region","high","guardduty","AwsGuardDutyDetector","logging",
  {"nist_800_53_revision_5":["SI-4"],"pci_dss_v4_0":["11.5.1"],"aws_foundational_security":["GuardDuty.1"],"soc2":["CC7.2"]},
  "Enable GuardDuty in every active region (use delegated administrator at the org level).","https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_settingup.html"),
 ("securityhub_enabled","Security Hub is not enabled in the region","medium","securityhub","AwsSecurityHubHub","logging",
  {"cis_3_0_aws":["4.16"],"nist_800_53_revision_5":["CA-7"]},
  "Enable Security Hub with the AWS Foundational Security Best Practices standard.","https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-settingup.html"),
 ("secretsmanager_automatic_rotation_enabled","Secrets Manager secret has rotation disabled","medium","secretsmanager","AwsSecretsManagerSecret","iam",
  {"nist_800_53_revision_5":["IA-5(1)"],"pci_dss_v4_0":["8.3.9"],"aws_foundational_security":["SecretsManager.1"]},
  "Configure a rotation Lambda and a rotation schedule for the secret.","https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html"),
 ("elbv2_listeners_underneath_https","Load balancer listener uses HTTP without redirect to HTTPS","medium","elb","AwsElbv2LoadBalancer","network",
  {"nist_800_53_revision_5":["SC-8"],"pci_dss_v4_0":["4.2.1"],"aws_foundational_security":["ELB.1"]},
  "Redirect HTTP to HTTPS and attach an ACM certificate to the listener.","https://docs.aws.amazon.com/elasticloadbalancing/latest/application/create-https-listener.html"),
]
GCP = [
 ("cloudstorage_bucket_public_access","Cloud Storage bucket is publicly accessible","critical","cloudstorage","Bucket","storage",
  {"cis_3_0_gcp":["5.1"],"pci_dss_v4_0":["1.3.1"],"iso27001_2022_gcp":["A.8.3"],"soc2":["CC6.1"]},
  "Remove allUsers/allAuthenticatedUsers bindings and enforce public access prevention.","https://cloud.google.com/storage/docs/public-access-prevention"),
 ("cloudstorage_bucket_uniform_bucket_level_access","Bucket does not enforce uniform bucket-level access","medium","cloudstorage","Bucket","storage",
  {"cis_3_0_gcp":["5.2"],"iso27001_2022_gcp":["A.8.3"]},
  "Enable uniform bucket-level access on the bucket.","https://cloud.google.com/storage/docs/uniform-bucket-level-access"),
 ("compute_firewall_ssh_access_from_the_internet_allowed","Firewall rule allows SSH (22) from 0.0.0.0/0","high","compute","FirewallRule","network",
  {"cis_3_0_gcp":["3.6"],"pci_dss_v4_0":["1.3.1"],"iso27001_2022_gcp":["A.8.20"]},
  "Restrict the source range to trusted CIDRs or use IAP TCP forwarding.","https://cloud.google.com/iap/docs/using-tcp-forwarding"),
 ("compute_firewall_rdp_access_from_the_internet_allowed","Firewall rule allows RDP (3389) from 0.0.0.0/0","high","compute","FirewallRule","network",
  {"cis_3_0_gcp":["3.7"],"pci_dss_v4_0":["1.3.1"]},
  "Restrict the source range to trusted CIDRs or use IAP TCP forwarding.","https://cloud.google.com/iap/docs/using-tcp-forwarding"),
 ("compute_instance_public_ip","Compute instance has an external IP address","medium","compute","Instance","network",
  {"cis_3_0_gcp":["4.9"],"iso27001_2022_gcp":["A.8.20"]},
  "Remove the external IP and use Cloud NAT / IAP for egress and access.","https://cloud.google.com/nat/docs/overview"),
 ("compute_instance_default_service_account_in_use","Instance uses the default Compute Engine service account","medium","compute","Instance","iam",
  {"cis_3_0_gcp":["4.1"],"iso27001_2022_gcp":["A.5.15"]},
  "Create a dedicated least-privilege service account and attach it to the instance.","https://cloud.google.com/compute/docs/access/service-accounts"),
 ("compute_project_os_login_enabled","OS Login is not enabled at the project level","medium","compute","Project","iam",
  {"cis_3_0_gcp":["4.4"]},
  "Set enable-oslogin=TRUE in project metadata.","https://cloud.google.com/compute/docs/oslogin/set-up-oslogin"),
 ("compute_instance_serial_ports_in_use","Serial port access is enabled on the instance","low","compute","Instance","compute",
  {"cis_3_0_gcp":["4.5"]},
  "Set serial-port-enable=FALSE in instance metadata.","https://cloud.google.com/compute/docs/troubleshooting/troubleshooting-using-serial-console"),
 ("cloudsql_instance_public_ip","Cloud SQL instance has a public IP","high","cloudsql","Instance","network",
  {"cis_3_0_gcp":["6.6"],"pci_dss_v4_0":["1.3.1"],"iso27001_2022_gcp":["A.8.20"]},
  "Disable the public IP and connect via private IP or the Cloud SQL Auth Proxy.","https://cloud.google.com/sql/docs/mysql/configure-private-ip"),
 ("cloudsql_instance_ssl_connections","Cloud SQL instance does not require SSL","medium","cloudsql","Instance","encryption",
  {"cis_3_0_gcp":["6.4"],"pci_dss_v4_0":["4.2.1"]},
  "Set ssl_mode to ENCRYPTED_ONLY / TRUSTED_CLIENT_CERTIFICATE_REQUIRED.","https://cloud.google.com/sql/docs/mysql/configure-ssl-instance"),
 ("cloudsql_instance_automated_backups","Cloud SQL automated backups are disabled","medium","cloudsql","Instance","compute",
  {"cis_3_0_gcp":["6.7"],"soc2":["A1.2"]},
  "Enable automated backups and point-in-time recovery.","https://cloud.google.com/sql/docs/mysql/backup-recovery/backups"),
 ("iam_sa_user_managed_key_rotation_90_days","Service account key older than 90 days","medium","iam","ServiceAccountKey","iam",
  {"cis_3_0_gcp":["1.7"],"pci_dss_v4_0":["8.3.9"],"iso27001_2022_gcp":["A.5.17"]},
  "Rotate the key; prefer Workload Identity Federation over downloaded keys.","https://cloud.google.com/iam/docs/best-practices-for-managing-service-account-keys"),
 ("iam_sa_no_administrative_privileges","Service account has Owner/Editor/admin role","high","iam","ServiceAccount","iam",
  {"cis_3_0_gcp":["1.5"],"iso27001_2022_gcp":["A.8.2"],"soc2":["CC6.3"]},
  "Replace primitive roles with predefined least-privilege roles.","https://cloud.google.com/iam/docs/using-iam-securely"),
 ("kms_key_rotation_enabled","KMS key has no rotation period","medium","kms","CryptoKey","encryption",
  {"cis_3_0_gcp":["1.10"],"pci_dss_v4_0":["3.7.4"]},
  "Set a rotation period of at most 90 days on the key.","https://cloud.google.com/kms/docs/key-rotation"),
 ("logging_sink_created","No log sink exports all admin/data access logs","medium","logging","Project","logging",
  {"cis_3_0_gcp":["2.2"],"pci_dss_v4_0":["10.2.1"],"soc2":["CC7.2"]},
  "Create an aggregated sink to a locked Cloud Storage bucket or BigQuery dataset.","https://cloud.google.com/logging/docs/export/configure_export_v2"),
 ("logging_log_metric_filter_and_alert_for_project_ownership_changes_enabled","No alert for project ownership changes","low","logging","Project","logging",
  {"cis_3_0_gcp":["2.4"]},
  "Create a log-based metric and alert policy for ownership role changes.","https://cloud.google.com/logging/docs/logs-based-metrics"),
 ("gke_cluster_private_nodes","GKE cluster nodes have public IPs","high","gke","Cluster","network",
  {"cis_3_0_gcp":["6.6.5"],"iso27001_2022_gcp":["A.8.20"]},
  "Recreate the node pools as private nodes and enable a private endpoint.","https://cloud.google.com/kubernetes-engine/docs/how-to/private-clusters"),
 ("gke_cluster_no_default_service_account","GKE node pool uses the default service account","medium","gke","Cluster","iam",
  {"cis_3_0_gcp":["6.2.1"]},
  "Create a minimal service account for nodes and enable Workload Identity.","https://cloud.google.com/kubernetes-engine/docs/how-to/hardening-your-cluster#use_least_privilege_sa"),
 ("bigquery_dataset_public_access","BigQuery dataset is publicly accessible","critical","bigquery","Dataset","storage",
  {"cis_3_0_gcp":["7.1"],"pci_dss_v4_0":["1.3.1"],"soc2":["CC6.1"]},
  "Remove allUsers/allAuthenticatedUsers from the dataset ACL.","https://cloud.google.com/bigquery/docs/dataset-access-controls"),
 ("apikeys_key_exists","Unrestricted API key exists in the project","medium","apikeys","ApiKey","iam",
  {"cis_3_0_gcp":["1.12"]},
  "Delete the key or restrict it by application and API.","https://cloud.google.com/docs/authentication/api-keys#securing"),
 ("dns_dnssec_disabled","Cloud DNS zone has DNSSEC disabled","low","dns","ManagedZone","network",
  {"cis_3_0_gcp":["3.3"]},
  "Enable DNSSEC on the managed zone.","https://cloud.google.com/dns/docs/dnssec-config"),
]
AZURE = [
 ("storage_blob_public_access_level_is_disabled","Storage account allows public blob access","critical","storage","StorageAccount","storage",
  {"cis_2_1_azure":["3.7"],"pci_dss_v4_0":["1.3.1"],"iso27001_2022_azure":["A.8.3"],"soc2":["CC6.1"]},
  "Set allowBlobPublicAccess=false on the storage account.","https://learn.microsoft.com/azure/storage/blobs/anonymous-read-access-prevent"),
 ("storage_secure_transfer_required_is_enabled","Storage account does not require secure transfer","high","storage","StorageAccount","encryption",
  {"cis_2_1_azure":["3.1"],"pci_dss_v4_0":["4.2.1"]},
  "Enable 'Secure transfer required' on the storage account.","https://learn.microsoft.com/azure/storage/common/storage-require-secure-transfer"),
 ("storage_ensure_minimum_tls_version_12","Storage account allows TLS below 1.2","medium","storage","StorageAccount","encryption",
  {"cis_2_1_azure":["3.15"],"pci_dss_v4_0":["4.2.1"]},
  "Set the minimum TLS version to 1.2.","https://learn.microsoft.com/azure/storage/common/transport-layer-security-configure-minimum-version"),
 ("storage_infrastructure_encryption_is_enabled","Storage account infrastructure encryption is disabled","low","storage","StorageAccount","encryption",
  {"cis_2_1_azure":["3.2"]},
  "Recreate the account with infrastructure (double) encryption enabled.","https://learn.microsoft.com/azure/storage/common/infrastructure-encryption-enable"),
 ("network_ssh_internet_access_restricted","NSG allows SSH (22) from the internet","high","network","NetworkSecurityGroup","network",
  {"cis_2_1_azure":["6.1"],"pci_dss_v4_0":["1.3.1"],"iso27001_2022_azure":["A.8.20"]},
  "Restrict the inbound rule source to trusted ranges or use Azure Bastion.","https://learn.microsoft.com/azure/bastion/bastion-overview"),
 ("network_rdp_internet_access_restricted","NSG allows RDP (3389) from the internet","high","network","NetworkSecurityGroup","network",
  {"cis_2_1_azure":["6.2"],"pci_dss_v4_0":["1.3.1"]},
  "Restrict the inbound rule source to trusted ranges or use Azure Bastion.","https://learn.microsoft.com/azure/bastion/bastion-overview"),
 ("network_flow_log_more_than_90_days","NSG flow log retention is below 90 days","medium","network","NetworkSecurityGroup","logging",
  {"cis_2_1_azure":["6.5"],"pci_dss_v4_0":["10.5.1"]},
  "Set flow log retention to 90 days or more.","https://learn.microsoft.com/azure/network-watcher/nsg-flow-logs-overview"),
 ("network_watcher_enabled","Network Watcher is not enabled in the region","low","network","NetworkWatcher","logging",
  {"cis_2_1_azure":["6.6"]},
  "Enable Network Watcher for every region with resources.","https://learn.microsoft.com/azure/network-watcher/network-watcher-create"),
 ("sqlserver_tde_encryption_enabled","SQL database Transparent Data Encryption is off","high","sqlserver","SqlDatabase","encryption",
  {"cis_2_1_azure":["4.1.5"],"pci_dss_v4_0":["3.5.1"],"iso27001_2022_azure":["A.8.24"]},
  "Enable TDE on the database.","https://learn.microsoft.com/azure/azure-sql/database/transparent-data-encryption-tde-overview"),
 ("sqlserver_auditing_enabled","SQL server auditing is disabled","medium","sqlserver","SqlServer","logging",
  {"cis_2_1_azure":["4.1.1"],"pci_dss_v4_0":["10.2.1"],"soc2":["CC7.2"]},
  "Enable auditing to a Log Analytics workspace or storage account.","https://learn.microsoft.com/azure/azure-sql/database/auditing-overview"),
 ("sqlserver_azuread_administrator_enabled","SQL server has no Entra ID administrator","medium","sqlserver","SqlServer","iam",
  {"cis_2_1_azure":["4.1.4"]},
  "Configure an Entra ID admin for the SQL server.","https://learn.microsoft.com/azure/azure-sql/database/authentication-aad-configure"),
 ("defender_ensure_defender_for_servers_is_on","Defender for Servers is off","high","defender","Subscription","compute",
  {"cis_2_1_azure":["2.1.1"],"pci_dss_v4_0":["11.5.1"],"soc2":["CC7.2"]},
  "Enable Defender for Servers (Plan 2) on the subscription.","https://learn.microsoft.com/azure/defender-for-cloud/tutorial-enable-servers-plan"),
 ("defender_ensure_defender_for_storage_is_on","Defender for Storage is off","medium","defender","Subscription","storage",
  {"cis_2_1_azure":["2.1.6"]},
  "Enable Defender for Storage on the subscription.","https://learn.microsoft.com/azure/defender-for-cloud/tutorial-enable-storage-plan"),
 ("entra_privileged_user_has_mfa","Privileged Entra ID user has no MFA","critical","entra","User","iam",
  {"cis_2_1_azure":["1.1.2"],"pci_dss_v4_0":["8.4.2"],"iso27001_2022_azure":["A.5.17"],"soc2":["CC6.1"]},
  "Enforce MFA for privileged roles with a Conditional Access policy.","https://learn.microsoft.com/entra/identity/conditional-access/howto-conditional-access-policy-admin-mfa"),
 ("entra_users_mfa_capable","User is not registered for MFA","high","entra","User","iam",
  {"cis_2_1_azure":["1.1.3"],"pci_dss_v4_0":["8.4.2"]},
  "Require MFA registration via Conditional Access and security defaults.","https://learn.microsoft.com/entra/identity/authentication/howto-mfa-getstarted"),
 ("keyvault_key_expiration_set_in_non_rbac","Key Vault key has no expiration date","medium","keyvault","KeyVault","encryption",
  {"cis_2_1_azure":["8.1"],"pci_dss_v4_0":["3.7.4"]},
  "Set an expiration date on all keys and rotate before expiry.","https://learn.microsoft.com/azure/key-vault/keys/how-to-configure-key-rotation"),
 ("keyvault_logging_enabled","Key Vault diagnostic logging is disabled","medium","keyvault","KeyVault","logging",
  {"cis_2_1_azure":["5.1.5"],"soc2":["CC7.2"]},
  "Enable AuditEvent diagnostic settings to Log Analytics.","https://learn.microsoft.com/azure/key-vault/general/logging"),
 ("keyvault_rbac_enabled","Key Vault uses access policies instead of RBAC","low","keyvault","KeyVault","iam",
  {"cis_2_1_azure":["8.5"]},
  "Migrate the vault to the Azure RBAC permission model.","https://learn.microsoft.com/azure/key-vault/general/rbac-migration"),
 ("vm_ensure_attached_disks_encrypted_with_cmk","VM disk is not encrypted with a customer-managed key","medium","vm","Disk","encryption",
  {"cis_2_1_azure":["7.3"],"iso27001_2022_azure":["A.8.24"]},
  "Attach a disk encryption set backed by a Key Vault CMK.","https://learn.microsoft.com/azure/virtual-machines/disk-encryption"),
 ("vm_ensure_using_managed_disks","VM uses unmanaged disks","low","vm","VirtualMachine","compute",
  {"cis_2_1_azure":["7.2"]},
  "Migrate the VM to managed disks.","https://learn.microsoft.com/azure/virtual-machines/windows/convert-unmanaged-to-managed-disks"),
 ("aks_clusters_rbac_enabled","AKS cluster has Kubernetes RBAC disabled","high","aks","ManagedCluster","iam",
  {"cis_2_1_azure":["9.1"],"iso27001_2022_azure":["A.8.2"]},
  "Recreate the cluster with RBAC and Entra ID integration enabled.","https://learn.microsoft.com/azure/aks/manage-azure-rbac"),
 ("aks_network_policy_enabled","AKS cluster has no network policy","medium","aks","ManagedCluster","network",
  {"cis_2_1_azure":["9.3"]},
  "Enable Azure or Calico network policy on the cluster.","https://learn.microsoft.com/azure/aks/use-network-policies"),
 ("monitor_diagnostic_setting_with_appropriate_categories","Subscription activity log has no diagnostic setting","medium","monitor","Subscription","logging",
  {"cis_2_1_azure":["5.1.2"],"pci_dss_v4_0":["10.2.1"],"soc2":["CC7.2"]},
  "Create a diagnostic setting exporting Administrative, Security, Alert and Policy categories.","https://learn.microsoft.com/azure/azure-monitor/essentials/diagnostic-settings"),
 ("app_ensure_http_is_redirected_to_https","App Service allows HTTP traffic","medium","app","WebApp","network",
  {"cis_2_1_azure":["9.2"],"pci_dss_v4_0":["4.2.1"]},
  "Enable 'HTTPS Only' on the App Service.","https://learn.microsoft.com/azure/app-service/configure-ssl-bindings#enforce-https"),
]
CATALOG = {"aws": AWS, "gcp": GCP, "azure": AZURE}

# ---------------------------------------------------------------- resource naming
WORDS = ["payments","ledger","checkout","kyc","risk","fraud","reporting","analytics","ingest","warehouse",
         "customer","billing","notifications","auth","gateway","search","media","backup","exports","audit"]
ENVS = {"478915623094": "prod", "613920475168": "stg", "offload-prod-platform-481523": "prod",
        "7e3a9c14-2f6b-4d80-bb15-9a4e2c1f7d63": "prod"}

def res_for(provider, acct, region, rtype, i):
    w = WORDS[i % len(WORDS)]; env = ENVS.get(acct, "prod"); n = i + 1
    proj = acct if provider == "gcp" else None
    sub = acct if provider == "azure" else None
    rg = f"rg-{env}-{w}"
    m = {
      # aws
      "AwsS3Bucket": (f"offsec-{env}-{w}", f"arn:aws:s3:::offsec-{env}-{w}"),
      "AwsIamUser": ((f"root" if rtype=="AwsIamUser" and i==0 else f"{w}.svc"), f"arn:aws:iam::{acct}:user/{w}.svc"),
      "AwsIamAccessKey": (f"AKIA{hid(acct,w,n,n=16).upper()}", f"arn:aws:iam::{acct}:user/{w}.svc/AKIA{hid(acct,w,n,n=16).upper()}"),
      "AwsEc2SecurityGroup": (f"sg-{env}-{w}", f"arn:aws:ec2:{region}:{acct}:security-group/sg-0{hid(acct,w,n,n=16)}"),
      "AwsEc2Volume": (f"vol-{hid(acct,w,n,n=17)}", f"arn:aws:ec2:{region}:{acct}:volume/vol-0{hid(acct,w,n,n=16)}"),
      "AwsEc2Instance": (f"{env}-{w}-{n:02d}", f"arn:aws:ec2:{region}:{acct}:instance/i-0{hid(acct,w,n,n=16)}"),
      "AwsRdsDbInstance": (f"{env}-{w}-db", f"arn:aws:rds:{region}:{acct}:db:{env}-{w}-db"),
      "AwsCloudTrailTrail": ("management-events", f"arn:aws:cloudtrail:{region}:{acct}:trail/management-events"),
      "AwsEc2Vpc": (f"vpc-{env}-{w}", f"arn:aws:ec2:{region}:{acct}:vpc/vpc-0{hid(acct,w,n,n=16)}"),
      "AwsKmsKey": (f"alias/{env}-{w}", f"arn:aws:kms:{region}:{acct}:key/{uuid.UUID(hid(acct,w,n,n=32))}"),
      "AwsLambdaFunction": (f"{env}-{w}-handler", f"arn:aws:lambda:{region}:{acct}:function:{env}-{w}-handler"),
      "AwsEksCluster": (f"{env}-{w}-eks", f"arn:aws:eks:{region}:{acct}:cluster/{env}-{w}-eks"),
      "AwsGuardDutyDetector": (region, f"arn:aws:guardduty:{region}:{acct}:detector"),
      "AwsSecurityHubHub": (region, f"arn:aws:securityhub:{region}:{acct}:hub/default"),
      "AwsSecretsManagerSecret": (f"{env}/{w}/db-credentials", f"arn:aws:secretsmanager:{region}:{acct}:secret:{env}/{w}/db-credentials"),
      "AwsElbv2LoadBalancer": (f"{env}-{w}-alb", f"arn:aws:elasticloadbalancing:{region}:{acct}:loadbalancer/app/{env}-{w}-alb/{hid(acct,w,n)}"),
      # gcp
      "Bucket": (f"offsec-{env}-{w}-{hid(acct,n,n=4)}", f"//storage.googleapis.com/offsec-{env}-{w}-{hid(acct,n,n=4)}"),
      "FirewallRule": (f"allow-{w}-ingress", f"//compute.googleapis.com/projects/{proj}/global/firewalls/allow-{w}-ingress"),
      "Instance": (f"{env}-{w}-{n:02d}", f"//compute.googleapis.com/projects/{proj}/zones/{region}-b/instances/{env}-{w}-{n:02d}"),
      "Project": (proj, f"//cloudresourcemanager.googleapis.com/projects/{proj}"),
      "ServiceAccountKey": (f"{w}-sa key {hid(acct,w,n,n=8)}", f"//iam.googleapis.com/projects/{proj}/serviceAccounts/{w}-sa@{proj}.iam.gserviceaccount.com/keys/{hid(acct,w,n,n=40)}"),
      "ServiceAccount": (f"{w}-sa@{proj}.iam.gserviceaccount.com", f"//iam.googleapis.com/projects/{proj}/serviceAccounts/{w}-sa@{proj}.iam.gserviceaccount.com"),
      "CryptoKey": (f"{w}-key", f"//cloudkms.googleapis.com/projects/{proj}/locations/{region}/keyRings/{env}-ring/cryptoKeys/{w}-key"),
      "Cluster": (f"{env}-{w}-gke", f"//container.googleapis.com/projects/{proj}/locations/{region}/clusters/{env}-{w}-gke"),
      "Dataset": (f"{w}_{env}", f"//bigquery.googleapis.com/projects/{proj}/datasets/{w}_{env}"),
      "ApiKey": (f"{w}-web-key", f"//apikeys.googleapis.com/projects/{proj}/locations/global/keys/{hid(acct,w,n,n=20)}"),
      "ManagedZone": (f"{w}-zone", f"//dns.googleapis.com/projects/{proj}/managedZones/{w}-zone"),
      # azure
      "StorageAccount": (f"st{env}{w}{hid(acct,n,n=4)}", f"/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/st{env}{w}{hid(acct,n,n=4)}"),
      "NetworkSecurityGroup": (f"nsg-{env}-{w}", f"/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Network/networkSecurityGroups/nsg-{env}-{w}"),
      "NetworkWatcher": (f"NetworkWatcher_{region}", f"/subscriptions/{sub}/resourceGroups/NetworkWatcherRG/providers/Microsoft.Network/networkWatchers/NetworkWatcher_{region}"),
      "SqlDatabase": (f"sqldb-{env}-{w}", f"/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Sql/servers/sql-{env}-{w}/databases/sqldb-{env}-{w}"),
      "SqlServer": (f"sql-{env}-{w}", f"/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Sql/servers/sql-{env}-{w}"),
      "Subscription": ("Enterprise Subscription (prod)", f"/subscriptions/{sub}"),
      "User": (f"{w}.admin@offloadsecurity.com", f"/users/{uuid.UUID(hid(acct,w,n,n=32))}"),
      "KeyVault": (f"kv-{env}-{w}", f"/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.KeyVault/vaults/kv-{env}-{w}"),
      "Disk": (f"disk-{env}-{w}-os", f"/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Compute/disks/disk-{env}-{w}-os"),
      "VirtualMachine": (f"vm-{env}-{w}-{n:02d}", f"/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Compute/virtualMachines/vm-{env}-{w}-{n:02d}"),
      "ManagedCluster": (f"aks-{env}-{w}", f"/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.ContainerService/managedClusters/aks-{env}-{w}"),
      "WebApp": (f"app-{env}-{w}", f"/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Web/sites/app-{env}-{w}"),
    }
    return m[rtype]

# How many failing resources a check typically hits (per account weight)
def fan_out(sev, weight):
    base = {"critical": (1, 3), "high": (2, 4), "medium": (2, 6), "low": (1, 5)}[sev]
    lo, hi = base
    return max(1, round(rng.randint(lo, hi) * weight))

# Prowler emits framework names like "CIS-3.0"; the ingestor lowercases them.
_FW_RENAME = {"cis_3_0_aws": "cis-3.0", "cis_3_0_gcp": "cis-3.0", "cis_2_1_azure": "cis-2.1",
              "nist_800_53_revision_5": "nist-800-53-revision-5", "pci_dss_v4_0": "pci-4.0",
              "aws_foundational_security": "aws-foundational-security-best-practices",
              "iso27001_2022_aws": "iso27001-2022", "iso27001_2022_gcp": "iso27001-2022", "iso27001_2022_azure": "iso27001-2022",
              "mitre_attack": "mitre-attack", "soc2": "soc2"}
def prowler_frameworks(fws, category, provider):
    out = {_FW_RENAME.get(k, k): v for k, v in fws.items()}
    if "nist-800-53-revision-5" in out: out.setdefault("nist-csf-2.0", ["PR.AA-05" if category == "iam" else "PR.DS-01"])
    if category in ("encryption", "storage"): out.setdefault("hipaa", ["164_312_a_2_iv"]); out.setdefault("gdpr", ["article_32"])
    if category in ("iam", "logging"): out.setdefault("rbi-cyber-security-framework", ["annex_i_1_3" if category == "iam" else "annex_i_5_1"])
    if provider == "azure" and category == "logging": out.setdefault("nis2", ["article_21_2_b"])
    if provider != "aws" and category == "network": out.setdefault("mitre-attack", ["T1190"])
    return out
_GROUP_PREFIX = (("cis","cis"),("nist-csf","nist"),("nist","nist"),("pci","pci"),("soc2","soc2"),("hipaa","hipaa"),("iso27001","iso"),
                 ("gdpr","gdpr"),("rbi","rbi"),("mitre","mitre"),("aws-foundational","aws_fsbp"),("nis2","nis"))
def framework_groups(fws):
    g = {}
    for k in fws:
        for pre, grp in _GROUP_PREFIX:
            if k.startswith(pre): g.setdefault(grp, []).append(k); break
    return {k: sorted(set(v)) for k, v in g.items()}

ACCOUNT_PLAN = {  # weight of failing findings, pass ratio, latest run status
    "478915623094": dict(weight=1.9, pass_ratio=1.15, latest="completed", scan_type="full"),
    "613920475168": dict(weight=1.0, pass_ratio=0.9, latest="running", scan_type="incremental"),
    "offload-prod-platform-481523": dict(weight=1.3, pass_ratio=1.1, latest="completed", scan_type="full"),
    "7e3a9c14-2f6b-4d80-bb15-9a4e2c1f7d63": dict(weight=1.2, pass_ratio=1.0, latest="partial", scan_type="full"),
}

def main():
    url = os.environ["MONGO_URL"]
    c = MongoClient(url)
    cs, orch, assets_db, plat, nat = c["cspm_cloud_security"], c["cspm_orchestration"], c["cspm_cloud_assets"], c["cspm_platform"], c["cspm_security_scans"]

    accts = list(cs.enhanced_cloud_accounts.find({"team_id": TEAM}))
    drop = [a["account_id"] for a in accts if a["account_id"] not in KEEP]
    if drop:
        cs.enhanced_cloud_accounts.delete_many({"team_id": TEAM, "account_id": {"$in": drop}})
        print("pruned accounts:", drop)
    accts = [a for a in accts if a["account_id"] in KEEP]
    assert len(accts) == 4, [a["account_id"] for a in accts]

    # wipe what we own
    print("wipe:", orch.scan_runs.delete_many({"team_id": TEAM}).deleted_count, "scan_runs;",
          cs.findings.delete_many({"team_id": TEAM}).deleted_count, "findings;",
          cs.compliance_scores.delete_many({"team_id": TEAM}).deleted_count, "scores;",
          cs.remediation_tasks.delete_many({"team_id": TEAM}).deleted_count, "tasks;",
          assets_db.assets.delete_many({"team_id": TEAM}).deleted_count, "assets;",
          plat.cloud_events.delete_many({}).deleted_count, "events;",
          nat.scan_results.delete_many({"tool_type": "cloud_scan", "metadata.team_id": TEAM}).deleted_count, "mirrors;",
          plat.iam_identities.delete_many({"team_id": TEAM}).deleted_count, "identities")

    all_runs, all_findings, all_scores, all_tasks, all_assets, all_events, all_identities = [], [], [], [], [], [], []

    for a in accts:
        acct, prov = a["account_id"], a["provider"]
        plan = ACCOUNT_PLAN[acct]
        regions = a.get("regions") or [a.get("region") or "global"]
        job_regions = regions if prov == "aws" else ["global"]
        catalog = CATALOG[prov]

        # ---- scan history: ~30 days, weekly full + incrementals
        history = []
        for d in (28, 21, 14, 7):
            history.append(("full", ago(days=d, hours=2), "completed"))
        for d in (3, 2):
            history.append(("incremental", ago(days=d, hours=1), "completed"))
        latest_status = plan["latest"]
        latest_at = ago(hours=6) if latest_status != "running" else ago(minutes=14)
        history.append((plan["scan_type"], latest_at, latest_status))
        latest_run_id = None
        for scan_type, started, status in history:
            run_id = str(uuid.UUID(hid(acct, scan_type, started.isoformat(), n=32)))
            dur = {"full": 1620, "incremental": 540, "quick": 240}.get(scan_type, 900) + rng.randint(-120, 240)
            if prov != "aws": dur = int(dur * 0.7)
            done = status != "running"
            completed = started + timedelta(seconds=dur) if done else None
            sub_jobs, region_status = [], []
            for r in job_regions:
                for jt, tool, prio in (("asset_discovery", "native_cloud_api", 1), ("compliance_scan", "prowler", 2)):
                    js = "completed"
                    err = None
                    if status == "running":
                        js = "completed" if jt == "asset_discovery" else ("running" if r == job_regions[0] else "queued")
                    if status == "partial" and jt == "compliance_scan" and r == job_regions[-1]:
                        js, err = "failed", "AuthorizationFailed: the service principal lacks Microsoft.Security/assessments/read (Defender for Cloud)"
                    sub_jobs.append({
                        "job_id": str(uuid.UUID(hid(run_id, r, jt, n=32))), "job_type": jt, "tool": tool,
                        "status": js, "progress": 100 if js == "completed" else (62 if js == "running" else 0),
                        "region": r, "priority": prio, "retry_count": 0 if js != "failed" else 3, "max_retries": 3,
                        "depends_on": [], "dispatched": js != "queued", "dispatched_at": started,
                        "started_at": started if js != "queued" else None,
                        "completed_at": (completed or NOW) if js in ("completed", "failed") else None,
                        "metrics": {}, "error_message": err, "updated_at": completed or NOW,
                    })
                for jt in ("kubernetes_cluster_discovery", "container_registry_discovery"):
                    if r != job_regions[0]: continue
                    sub_jobs.append({"job_id": str(uuid.UUID(hid(run_id, jt, n=32))), "job_type": jt, "tool": "native_cloud_api",
                        "status": "completed", "progress": 100, "region": None, "priority": 3, "retry_count": 0, "max_retries": 3,
                        "depends_on": [], "dispatched": True, "dispatched_at": started, "started_at": started,
                        "completed_at": started + timedelta(seconds=90), "metrics": {}, "error_message": None, "updated_at": started + timedelta(seconds=90)})
            # region_status
            for r in job_regions:
                rs = "completed"
                if status == "running": rs = "running" if r == job_regions[0] else "queued"
                if status == "partial" and r == job_regions[-1]: rs = "failed"
                region_status.append({"region": r, "status": rs, "progress": 100 if rs == "completed" else (62 if rs == "running" else 0),
                                      "assets_discovered": 0, "findings_count": 0, "started_at": started, "completed_at": completed})
            overall = 100 if done else 62
            run = {
                "run_id": run_id, "account_id": acct, "provider": prov, "scan_type": scan_type, "status": status,
                "progress": {"overall": overall, "discovery": 100 if done or status == "running" else 0,
                             "compliance": 100 if done else 35, "steampipe": 100, "prowler": 100 if done else 35},
                "sub_jobs": sub_jobs, "region_status": region_status, "artifacts": {},
                "summary": {"total_assets": 0, "total_findings": 0, "critical_findings": 0, "high_findings": 0, "medium_findings": 0, "low_findings": 0},
                "errors": [], "warnings": [], "started_at": started, "completed_at": completed,
                "estimated_completion": (started + timedelta(seconds=dur)) if not done else None,
                "scan_duration_seconds": dur if done else None, "created_at": started - timedelta(seconds=8),
                "updated_at": completed or NOW, "created_by": USER, "team_id": TEAM, "user_id": USER,
                "api_calls_made": rng.randint(1800, 9400), "retry_count": 0,
                "regions": job_regions, "scan_config": {"regions": job_regions, "scan_type": scan_type},
            }
            if status == "partial":
                run["warnings"].append({"code": "permission_denied", "region": job_regions[-1],
                    "message": "Defender for Cloud assessments could not be read — grant 'Security Reader' to the service principal. Other checks completed."})
            history_run = run
            all_runs.append(run)
            if done and status in ("completed", "partial"):
                latest_completed = run
            latest_run_id = run_id
        base_run = latest_completed  # findings are stamped with the latest finished run
        base_time = base_run["completed_at"]

        # ---- findings for this account
        sev_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        fw_scores = {}
        n_fail = 0
        for ci, (check_id, title, sev, service, rtype, category, fws0, rem_text, rem_url) in enumerate(catalog):
            fws = prowler_frameworks(fws0, category, prov)
            # a slice of checks passes entirely in this account
            passes_entirely = rng.random() < (plan["pass_ratio"] * 0.35)
            count = fan_out(sev, plan["weight"])
            # single-resource checks
            if rtype in ("AwsIamUser", "AwsCloudTrailTrail", "Project", "Subscription", "AwsSecurityHubHub", "AwsGuardDutyDetector", "NetworkWatcher"):
                count = 1 if rtype not in ("AwsGuardDutyDetector", "AwsSecurityHubHub", "NetworkWatcher") else min(count, len(job_regions))
            for i in range(count):
                region = job_regions[i % len(job_regions)] if prov == "aws" else (a.get("region") or "global")
                name, uid = res_for(prov, acct, region, rtype, i + ci)
                p_pass = plan["pass_ratio"] * (0.2 if sev == "critical" else 0.35 if sev == "high" else 0.5)
                status = "pass" if (passes_entirely and sev != "critical") or rng.random() < p_pass else "fail"
                first_seen_days = rng.choice([28, 28, 21, 21, 14, 7, 7, 3, 2, 0])
                detected = ago(days=first_seen_days, hours=2) if first_seen_days else base_time
                doc = {
                    "finding_id": f"finding_{hid(TEAM, acct, check_id, uid)}",
                    "scan_run_id": base_run["run_id"], "artifact_id": f"artifact_{prov}_{acct}_{base_time:%Y%m%d}",
                    "dedup_key": f"{prov}|{acct}|{check_id}|{uid}", "provider": prov, "account_id": acct,
                    "region": region, "category": category, "team_id": TEAM, "check_id": check_id, "check_title": title,
                    "service": service, "resource_type": rtype, "resource_uid": uid, "resource_name": name,
                    "status": status, "severity": sev, "severity_rank": SEV_RANK[sev], "risk_score": SEV_SCORE[sev],
                    "resolved_at": None, "resolved_in_scan": None,
                    "description": (f"{title}: {name}" if status == "fail" else f"{name} is compliant: {title.replace(' has ', ' does not have ').replace(' is ', ' is not ')}"),
                    "compliance_frameworks": fws, "framework_groups": framework_groups(fws),
                    "remediation": {"text": rem_text, "url": rem_url, "complexity": "medium"},
                    "asset_id": None, "detected_at": detected, "last_seen": base_time, "first_seen": detected,
                }
                # sprinkle lifecycle states onto failing findings
                if status == "fail":
                    r = rng.random()
                    if r < 0.06 and sev in ("low", "medium"):
                        doc.update({"status": "suppressed", "suppressed_at": ago(days=rng.randint(1, 10)), "suppressed_by": USER,
                                    "suppress_until": NOW + timedelta(days=rng.choice([14, 30, 60])),
                                    "suppression_reason": rng.choice(["Accepted risk — legacy batch host, decommission scheduled Q4",
                                                                       "False positive — resource is internal-only behind private link",
                                                                       "Compensating control: WAF + IP allow-list in front of the endpoint"])})
                    elif r < 0.14:
                        rd = ago(days=rng.randint(1, 12))
                        doc.update({"status": "resolved", "resolved_at": rd, "resolved_in_scan": base_run["run_id"], "resolved_by": USER,
                                    "resolution_notes": "Fixed by platform team; verified in follow-up scan."})
                    else:
                        n_fail += 1; sev_counts[sev] += 1
                        if r > 0.84 and sev in ("critical", "high"):
                            # open remediation task
                            all_tasks.append({
                                "task_id": f"task_{hid(doc['finding_id'])}", "finding_id": doc["finding_id"], "check_id": check_id,
                                "finding_title": title, "resource_id": uid, "severity": sev, "account_id": acct, "provider": prov,
                                "assigned_to": rng.choice(["platform-team", "cloud-sre", "security-eng", "data-platform"]),
                                "priority": "high" if sev == "critical" else "medium", "status": rng.choice(["open", "open", "in_progress", "in_progress", "done"]),
                                "due_date": (NOW + timedelta(days=rng.choice([3, 7, 14]))).strftime("%Y-%m-%d"),
                                "notes": rng.choice(["Ticketed to owning team; change window Thursday.", "Needs Terraform change in infra repo.", ""]),
                                "created_by": USER, "created_at": ago(days=rng.randint(0, 5)), "team_id": TEAM,
                            })
                            doc["remediation_task_id"] = all_tasks[-1]["task_id"]
                # per-framework score bookkeeping (pass/fail of active findings only)
                if doc["status"] in ("pass", "fail"):
                    for fw in fws:
                        s = fw_scores.setdefault(fw, {"total": 0, "passed": 0, "failed": 0, "by_sev": {}})
                        s["total"] += 1
                        b = s["by_sev"].setdefault(sev, {"passed": 0, "failed": 0})
                        if doc["status"] == "pass": s["passed"] += 1; b["passed"] += 1
                        else: s["failed"] += 1; b["failed"] += 1
                all_findings.append(doc)

        # compliance scores for latest finished run
        for fw, s in fw_scores.items():
            all_scores.append({"score_id": f"score_{base_run['run_id']}_{fw}", "scan_run_id": base_run["run_id"], "account_id": acct,
                "provider": prov, "framework": fw, "region": "global", "team_id": TEAM,
                "score": round(s["passed"] / s["total"] * 100, 2), "total_checks": s["total"], "passed_checks": s["passed"],
                "failed_checks": s["failed"], "by_severity": s["by_sev"], "calculated_at": base_time})

        # ---- assets for this account
        n_assets = {"478915623094": 46, "613920475168": 22, "offload-prod-platform-481523": 30, "7e3a9c14-2f6b-4d80-bb15-9a4e2c1f7d63": 26}[acct]
        asset_types = {
            "aws": [("aws:ec2_instance","ec2","ec2_instance","running"),("aws:s3_bucket","s3","s3_bucket","active"),("aws:rds_instance","rds","rds_instance","available"),
                    ("aws:lambda_function","lambda","lambda_function","active"),("aws:iam_role","iam","iam_role","active"),("aws:security_group","ec2","security_group","active"),
                    ("aws:eks_cluster","eks","eks_cluster","active"),("aws:kms_key","kms","kms_key","enabled"),("aws:vpc","ec2","vpc","available")],
            "gcp": [("gcp:compute_instance","compute","compute_instance","running"),("gcp:storage_bucket","storage","storage_bucket","active"),("gcp:cloudsql_instance","cloudsql","cloudsql_instance","runnable"),
                    ("gcp:gke_cluster","gke","gke_cluster","running"),("gcp:service_account","iam","service_account","active"),("gcp:bigquery_dataset","bigquery","bigquery_dataset","active"),("gcp:firewall_rule","compute","firewall_rule","active")],
            "azure": [("azure:virtual_machine","compute","virtual_machine","running"),("azure:storage_account","storage","storage_account","available"),("azure:sql_database","sql","sql_database","online"),
                      ("azure:key_vault","keyvault","key_vault","active"),("azure:aks_cluster","aks","aks_cluster","succeeded"),("azure:network_security_group","network","network_security_group","active"),("azure:app_service","app","app_service","running")],
        }[prov]
        for i in range(n_assets):
            at, svc, rt, st = asset_types[i % len(asset_types)]
            region = regions[i % len(regions)]
            w = WORDS[i % len(WORDS)]; env = ENVS[acct]
            nm = f"{env}-{w}-{i//len(asset_types)+1:02d}" if rt not in ("s3_bucket","storage_bucket","storage_account") else (f"offsec-{env}-{w}" if prov != "azure" else f"st{env}{w}{i:02d}")
            native = {"aws": f"arn:aws:{svc}:{region}:{acct}:{rt}/{nm}", "gcp": f"//{svc}.googleapis.com/projects/{acct}/{rt}s/{nm}",
                      "azure": f"/subscriptions/{acct}/resourceGroups/rg-{env}-{w}/providers/{rt}/{nm}"}[prov]
            public = rt in ("ec2_instance","compute_instance","virtual_machine","app_service") and i % 4 == 0
            all_assets.append({
                "asset_id": str(uuid.UUID(hid(TEAM, acct, native, n=32))), "team_id": TEAM, "provider": prov, "account_id": acct,
                "region": region, "asset_type": at, "native_id": native, "name": nm, "service": svc, "resource_type": rt, "status": st,
                "tags": {"Name": nm, "Environment": "production" if env == "prod" else "staging", "Team": rng.choice(["platform","payments","data","sre"]), "CostCenter": rng.choice(["CC-1042","CC-2210","CC-3305"])},
                "metadata": {"public": public, "encrypted": (i % 5 != 0), "arn": native},
                "is_public": public, "encrypted": (i % 5 != 0), "risk_level": rng.choice(["low","low","medium","high"]),
                "discovered_at": ago(days=rng.choice([28, 21, 14, 7])), "last_seen": base_time, "first_seen": ago(days=28),
                "discovery_method": {"aws": "native_cloud_api", "gcp": "cloud_asset_inventory", "azure": "resource_graph"}[prov],
                "scan_run_id": base_run["run_id"], "created_at": ago(days=28), "updated_at": base_time,
            })

        # ---- stamp run summaries + account rollups
        for run in all_runs:
            if run["account_id"] != acct: continue
            if run["status"] in ("completed", "partial"):
                scale = 1.0 if run["run_id"] == base_run["run_id"] else rng.uniform(0.85, 1.15)
                run["summary"] = {"total_assets": n_assets, "total_findings": int(n_fail * scale),
                                  "critical_findings": int(sev_counts["critical"] * scale), "high_findings": int(sev_counts["high"] * scale),
                                  "medium_findings": int(sev_counts["medium"] * scale), "low_findings": int(sev_counts["low"] * scale)}
                per = max(1, len(run["region_status"]))
                for rs in run["region_status"]:
                    rs["assets_discovered"] = n_assets // per; rs["findings_count"] = run["summary"]["total_findings"] // per
        cs.enhanced_cloud_accounts.update_one({"_id": a["_id"]}, {"$set": {
            "last_scan": base_time, "last_scanned_at": base_time, "last_inventory_update": base_time, "updated_at": NOW,
            "resource_count": n_assets, "status": "active", "health_check_status": "healthy",
            "last_scan_run_id": latest_run_id, "last_scan_status": plan["latest"],
            "findings_summary": {"total": n_fail, **sev_counts}}})

        # ---- identity roster (CIEM) for this account
        ident_plan = {
            "aws":   [("iam_user", "{w}.svc"), ("iam_role", "{env}-{w}-role"), ("iam_user", "{w}.admin")],
            "gcp":   [("service_account", "{w}-sa@{acct}.iam.gserviceaccount.com"), ("user", "{w}.admin@offloadsecurity.com")],
            "azure": [("service_principal", "sp-{env}-{w}"), ("user", "{w}.admin@offloadsecurity.com"), ("managed_identity", "mi-{env}-{w}")],
        }[prov]
        n_ident = {"aws": 14, "gcp": 9, "azure": 9}[prov]
        for i in range(n_ident):
            itype, tmpl = ident_plan[i % len(ident_plan)]
            w = WORDS[(i * 3) % len(WORDS)]; env = ENVS[acct]
            name = tmpl.format(w=w, env=env, acct=acct)
            is_admin = (i % 7 == 0)
            over = (not is_admin) and (i % 4 == 1)
            days = rng.choice([0, 1, 2, 5, 9, 14, 33, 61, 97, 140, None])
            risk = "critical" if is_admin else ("high" if over else rng.choice(["low", "low", "medium"]))
            if days and days > 90 and risk == "low": risk = "medium"
            arn = {"aws": f"arn:aws:iam::{acct}:{'role' if itype == 'iam_role' else 'user'}/{name}",
                   "gcp": f"//iam.googleapis.com/projects/{acct}/serviceAccounts/{name}" if itype == "service_account" else f"user:{name}",
                   "azure": f"/subscriptions/{acct}/providers/Microsoft.ManagedIdentity/{name}" if itype == "managed_identity" else f"/servicePrincipals/{uuid.UUID(hid(acct, name, n=32))}"}[prov]
            sev = "critical" if is_admin else "high" if over else risk
            all_identities.append({
                "team_id": TEAM, "provider": prov, "account_id": acct, "native_id": name, "name": name,
                "identity_type": itype, "arn": arn, "is_admin": is_admin, "is_overprivileged": over,
                "risk_level": risk, "severity": sev,
                "last_used": (NOW - timedelta(days=days)).isoformat() if days is not None else "unknown",
                "days_since_used": days, "last_analyzed_at": base_time, "updated_at": base_time, "first_seen": ago(days=28),
            })

        # ---- cloud events (recent activity)
        ev_catalog = {
            "aws": [("DeleteTrail","critical","logging","cloudtrail"),("PutBucketPolicy","high","storage","s3"),("AuthorizeSecurityGroupIngress","high","network","ec2"),
                    ("CreateUser","medium","iam","iam"),("AttachUserPolicy","high","iam","iam"),("StopLogging","critical","logging","cloudtrail"),
                    ("ModifyDBInstance","medium","database","rds"),("ConsoleLogin","low","iam","signin"),("CreateAccessKey","medium","iam","iam"),("DisableKey","high","encryption","kms")],
            "gcp": [("SetIamPolicy","high","iam","cloudresourcemanager"),("v1.compute.firewalls.insert","high","network","compute"),("storage.setIamPermissions","high","storage","storage"),
                    ("google.iam.admin.v1.CreateServiceAccountKey","medium","iam","iam"),("v1.compute.instances.insert","low","compute","compute"),("DeleteSink","critical","logging","logging")],
            "azure": [("Microsoft.Network/networkSecurityGroups/securityRules/write","high","network","network"),("Microsoft.Authorization/roleAssignments/write","high","iam","authorization"),
                      ("Microsoft.Storage/storageAccounts/write","medium","storage","storage"),("Microsoft.KeyVault/vaults/accessPolicies/write","high","encryption","keyvault"),
                      ("Microsoft.Compute/virtualMachines/write","low","compute","compute"),("Microsoft.Insights/diagnosticSettings/delete","critical","logging","monitor")],
        }[prov]
        actors = ["deploy-bot", "priya.n@offloadsecurity.com", "terraform-ci", "arjun.m@offloadsecurity.com", "svc-data-platform"]
        for i in range(14 if prov == "aws" else 8):
            en, sev, dom, svc = ev_catalog[i % len(ev_catalog)]
            t = ago(hours=rng.randint(0, 72), minutes=rng.randint(0, 59))
            actor = actors[i % len(actors)]
            all_events.append({
                "event_id": str(uuid.uuid4()), "provider": prov, "event_name": en, "severity": sev, "domain": dom,
                "description": f"{en} by {actor} on {acct}", "actor": actor, "resource_id": f"{svc}/{WORDS[i % len(WORDS)]}",
                "region": regions[i % len(regions)], "account_id": acct, "finding_id": None, "status": "processed",
                "source_ip": f"10.{rng.randint(0,255)}.{rng.randint(0,255)}.{rng.randint(1,254)}" if "bot" in actor or "ci" in actor or "svc" in actor else f"49.{rng.randint(32,47)}.{rng.randint(0,255)}.{rng.randint(1,254)}",
                "user_agent": "aws-cli/2.17.5" if prov == "aws" else ("google-cloud-sdk" if prov == "gcp" else "AzureCLI/2.62"),
                "service_name": svc, "permissions": [en], "change_summary": f"{en} applied",
                "event_time": t, "received_at": t + timedelta(seconds=rng.randint(4, 40)), "team_id": TEAM,
            })

    orch.scan_runs.insert_many(all_runs)
    cs.findings.insert_many(all_findings)
    cs.compliance_scores.insert_many(all_scores)
    if all_tasks: cs.remediation_tasks.insert_many(all_tasks)
    assets_db.assets.insert_many(all_assets)
    plat.cloud_events.insert_many(all_events)
    plat.iam_identities.insert_many(all_identities)
    mirrors = []
    for run in all_runs:
        st = run["status"]
        meta = {"team_id": TEAM, "source": "cloud_scan_orchestration_service", "provider": run["provider"], "account_id": run["account_id"],
                "run_id": run["run_id"], "total_findings": run["summary"]["total_findings"], "total_assets": run["summary"]["total_assets"],
                "completed_sub_jobs": sum(1 for j in run["sub_jobs"] if j["status"] == "completed"),
                "failed_sub_jobs": sum(1 for j in run["sub_jobs"] if j["status"] == "failed"),
                "pending_at": run["created_at"].isoformat(), "running_at": run["started_at"].isoformat()}
        if run["completed_at"]: meta[f"{st}_at"] = run["completed_at"].isoformat()
        if st == "partial": meta["error"] = "1 of %d sub-jobs failed (permission denied)" % len(run["sub_jobs"])
        mirrors.append({"scan_id": run["run_id"], "created_at": run["created_at"].isoformat(), "updated_at": (run["completed_at"] or NOW).isoformat(),
                        "findings": [], "findings_count": run["summary"]["total_findings"], "metadata": meta,
                        "raw_output": {"summary": run["summary"], "provider": run["provider"], "account_id": run["account_id"],
                                       "total_assets": run["summary"]["total_assets"], "total_findings": run["summary"]["total_findings"]},
                        "scan_type": run["scan_type"], "status": st, "target": f"{run['provider']}:{run['account_id']}",
                        "tool_type": "cloud_scan", "user_id": USER, "team_id": TEAM})
    nat.scan_results.insert_many(mirrors)
    from collections import Counter
    print("runs", len(all_runs), Counter(r["status"] for r in all_runs))
    print("findings", len(all_findings), Counter(f["status"] for f in all_findings), Counter(f["severity"] for f in all_findings if f["status"] == "fail"))
    print("scores", len(all_scores), "tasks", len(all_tasks), "assets", len(all_assets), "events", len(all_events), "identities", len(all_identities))

if __name__ == "__main__":
    main()
