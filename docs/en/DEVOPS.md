# DevOps Guide

## Infrastructure as Code

```terraform
provider "aws" {
  region = "eu-west-1"
}

module "FinAsis_cluster" {
  source = "./modules/kubernetes"
  
  cluster_name    = "finasis-prod"
  node_count      = 5
  instance_type   = "t3.large"
}
```

## Monitoring Setup

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: finasis-monitor
spec:
  endpoints:
  - port: web
    interval: 15s
  selector:
    matchLabels:
      app: finasis
```

## Backup Strategy
- Daily: Full database backup
- Hourly: Transaction logs
- Weekly: System state backup
- Monthly: Archive to cold storage
