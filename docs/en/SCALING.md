# Scaling Strategies

## Infrastructure Scaling
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: finasis-trading-engine
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: trading-engine
  minReplicas: 3
  maxReplicas: 100
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Database Sharding
```sql
-- Sharding Configuration
CREATE TABLE users_shard (
    shard_id int,
    user_range int,
    db_connection varchar(255)
);

-- Shard Distribution
INSERT INTO users_shard VALUES
(1, 1000000, 'db-1.finasis.com'),
(2, 2000000, 'db-2.finasis.com');
```
