# Terraform: VPC + EKS on AWS

Creates a VPC with two public subnets in two availability zones, an EKS cluster and a managed node group of two `t3.medium` nodes (with the EBS CSI driver for the Postgres volume). No NAT gateway is used, so the nodes sit in the public subnets and the cost stays low.

Credentials come from the AWS CLI profile (`aws configure`); nothing secret is stored in this directory. Copy `terraform.tfvars.example` to `terraform.tfvars` to override defaults (the real file is git-ignored).

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

Remove the Helm releases that created load balancers first, then tear everything down so nothing keeps billing:

```bash
helm uninstall ingress-nginx -n ingress-nginx
terraform destroy
```
