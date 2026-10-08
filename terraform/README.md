# Terraform: VPC and EKS

Creates a VPC with two public subnets in two availability zones, an EKS cluster and a managed node group of `t3.small` nodes. There is no NAT gateway, so the nodes sit in the public subnets.

Credentials come from the AWS CLI profile. Copy `terraform.tfvars.example` to `terraform.tfvars` and set `api_access_cidrs` to your own public IP. That file is git-ignored.

```bash
terraform init
terraform validate
terraform plan -out=tfplan
terraform apply tfplan            # about 15 minutes
aws eks update-kubeconfig --region ap-south-1 --name placetrack
kubectl get nodes
terraform destroy                 # when done, so nothing keeps billing
```
