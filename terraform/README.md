# Terraform: VPC + EKS on AWS

Creates a VPC with two public subnets in two availability zones, an EKS cluster and a managed node group of two `t3.medium` nodes (with the EBS CSI driver for the Postgres volume). No NAT gateway is used, so the nodes sit in the public subnets and the cost stays low.

Credentials come from the AWS CLI profile (`aws configure`), so nothing secret is stored here. Copy `terraform.tfvars.example` to `terraform.tfvars` and set `api_access_cidrs` to your own public IP. That variable is required and the real file is git-ignored. The other values have defaults.

```bash
cd terraform
terraform init
terraform fmt -check
terraform validate
terraform plan -out=tfplan
terraform apply tfplan          # about 15 minutes
aws eks update-kubeconfig --region ap-south-1 --name placetrack
kubectl get nodes
```

To tear everything down, remove the load balancer first, then destroy:

```bash
helm uninstall ingress-nginx -n ingress-nginx
terraform destroy
```
