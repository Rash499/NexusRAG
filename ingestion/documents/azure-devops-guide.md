# Azure DevOps Infrastructure Deployment Guide

## Overview

This document describes a sample infrastructure deployment workflow using Azure DevOps, Terraform, and Microsoft Azure. The workflow demonstrates how Infrastructure as Code (IaC) can be combined with a Git-based CI/CD approach to provision and manage cloud infrastructure across multiple environments.

The example uses separate development and staging environments. Terraform manages the infrastructure, while Azure DevOps Pipelines automates validation, planning, deployment, and controlled destruction.

---

## Architecture

The deployment architecture contains the following components:

* Microsoft Azure subscription
* Azure Resource Groups
* Azure Storage Account for Terraform remote state
* Azure Key Vault
* Azure DevOps project
* Azure DevOps self-hosted agent
* Terraform
* Git repository
* Development environment
* Staging environment

The general workflow is:

```text
Developer
   |
   v
Git Repository
   |
   v
Azure DevOps Pipeline
   |
   +----> Terraform Validate
   |
   +----> Terraform Plan
   |
   v
Terraform Apply
   |
   v
Microsoft Azure
```

---

## Terraform Remote State

Terraform requires a state file to track resources that it manages. Instead of storing the state file locally, the project uses Azure Storage as a remote backend.

The development environment uses a storage account named:

`tfdevbackend2026rash`

The staging environment uses:

`tfstagebackend2026rash`

Both environments use a blob container named:

`tfstate`

Example state files include:

```text
dev.tfstate
stage.tfstate
```

Using remote state provides centralized state management and makes it easier for CI/CD pipelines to work with the same infrastructure state.

---

## Azure DevOps Agent

The deployment pipeline runs Terraform commands using an Azure DevOps self-hosted agent.

The agent is configured in a pool named:

`agentpool_1`

The self-hosted agent provides a controlled execution environment for Terraform and other deployment tools.

Before running infrastructure changes, the agent must have the required tools installed and authenticated access to Azure.

---

## Authentication

The pipeline authenticates with Azure using a service principal.

The service principal is granted the Contributor role at the required Azure subscription scope.

The pipeline should not store credentials directly inside the Git repository.

Sensitive values such as client secrets should be stored using secure mechanisms such as:

* Azure DevOps secret variables
* Variable groups
* Azure Key Vault
* Federated identity credentials

Secrets should never be committed to source control.

---

## Infrastructure as Code

Terraform is used to define Azure infrastructure declaratively.

A simplified Terraform configuration may contain resources such as:

```text
Resource Group
    |
    +---- Virtual Network
    |        |
    |        +---- Subnet
    |
    +---- Network Security Group
    |
    +---- Virtual Machine
```

Terraform allows the infrastructure configuration to be version-controlled alongside application and pipeline code.

This makes infrastructure changes easier to review, reproduce, and audit.

---

## Environment Separation

The project separates infrastructure into development and staging environments.

### Development

The development environment is used for testing infrastructure changes before they are promoted.

Typical resources include:

* Development resource groups
* Development virtual networks
* Development compute resources
* Development monitoring resources

The Terraform state is stored in:

`dev.tfstate`

### Staging

The staging environment represents an environment closer to production.

It is used to validate infrastructure changes before production deployment.

The Terraform state is stored in:

`stage.tfstate`

Separating state between environments prevents Terraform operations in one environment from accidentally modifying resources belonging to another environment.

---

## CI/CD Pipeline

The Azure DevOps pipeline follows a Git-based CI/CD approach.

A typical pipeline contains the following stages:

```text
Code Commit
     |
     v
Terraform Init
     |
     v
Terraform Validate
     |
     v
Terraform Plan
     |
     v
Approval
     |
     v
Terraform Apply
```

The `terraform plan` stage allows the team to review the infrastructure changes before they are applied.

The production or staging deployment can include an approval gate before `terraform apply`.

---

## Terraform Modules

Reusable Terraform modules can be used to avoid duplicating infrastructure configuration.

For example:

```text
terraform/
├── modules/
│   ├── networking/
│   ├── virtual-machine/
│   ├── monitoring/
│   └── aks/
│
├── environments/
│   ├── dev/
│   └── staging/
│
└── main.tf
```

Modules make it possible to reuse common infrastructure patterns while allowing environment-specific configuration.

---

## Kubernetes Integration

The infrastructure can optionally include Azure Kubernetes Service (AKS).

AKS provides a managed Kubernetes environment for deploying containerized applications.

A typical architecture is:

```text
Azure DevOps
     |
     v
Terraform
     |
     v
Azure Kubernetes Service
     |
     +---- Node Pool
     |
     +---- Kubernetes Services
     |
     +---- Application Pods
```

Terraform can provision the AKS infrastructure while Kubernetes manifests or Helm charts can manage workloads deployed to the cluster.

---

## Security Considerations

Infrastructure pipelines should follow security best practices.

Important controls include:

1. Store secrets outside source control.
2. Use least-privilege permissions for service principals.
3. Restrict network access using Network Security Groups.
4. Enable encryption for sensitive resources.
5. Use Azure Key Vault for secret management.
6. Enable monitoring and logging.
7. Review Terraform plans before applying changes.
8. Protect the main branch.
9. Require pull-request reviews for infrastructure changes.
10. Separate development, staging, and production environments.

---

## Monitoring

Azure monitoring services can be integrated into the infrastructure.

Common monitoring components include:

* Azure Monitor
* Log Analytics
* Application Insights
* Microsoft Defender for Cloud

Logs and metrics can be collected centrally to help identify infrastructure failures and security issues.

---

## Disaster Recovery

Infrastructure deployments should consider backup and recovery requirements.

Important considerations include:

* Resource redundancy
* Backup policies
* Recovery point objectives (RPO)
* Recovery time objectives (RTO)
* Geographic redundancy
* Infrastructure recreation using Terraform

Infrastructure as Code can simplify disaster recovery because the infrastructure configuration is stored as version-controlled code.

---

## Common Troubleshooting Scenarios

### Terraform State Lock

If Terraform reports a state lock problem, check whether another Terraform process is currently running.

Do not remove a state lock blindly because another deployment may still be modifying infrastructure.

---

### Authentication Failure

If Terraform cannot authenticate with Azure, verify:

* Service principal credentials
* Subscription ID
* Tenant ID
* Required Azure permissions
* Azure DevOps service connection configuration

---

### Pipeline Failure

When a pipeline fails, inspect the failed stage and review the Terraform command output.

Typical commands that can help during local troubleshooting include:

```bash
terraform init
terraform validate
terraform plan
```

---

## Recommended Workflow

A safe infrastructure deployment workflow is:

1. Create a feature branch.
2. Modify Terraform configuration.
3. Run `terraform fmt`.
4. Run `terraform validate`.
5. Commit the changes.
6. Create a pull request.
7. Review the Terraform plan.
8. Merge the approved changes.
9. Run the deployment pipeline.
10. Verify the Azure resources.
11. Monitor the deployed infrastructure.

---

## Key Technologies

The example project uses:

* Microsoft Azure
* Azure DevOps
* Terraform
* Git
* Git-based CI/CD
* Azure Key Vault
* Azure Storage
* Azure Kubernetes Service
* Azure Monitor
* Log Analytics
* Microsoft Defender for Cloud

---

## Summary

Combining Terraform with Azure DevOps provides an automated approach for managing Azure infrastructure. Remote Terraform state allows multiple deployment processes to work with centralized state, while CI/CD pipelines provide validation, planning, approval, and deployment stages.

Separating development and staging environments helps reduce deployment risk and keeps infrastructure changes isolated. Security controls such as least-privilege access, secret management, network restrictions, and approval gates should be incorporated into the deployment workflow.
