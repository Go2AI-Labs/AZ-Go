---
layout: default
title: Distributed Training
parent: Training & Deployment
nav_order: 2
permalink: /distributed-training
---

# Distributed Training

AZ-Go implements a distributed training system that allows you to leverage multiple machines for faster self-play game generation and model training.

## Architecture Overview

The distributed training system consists of:
- **Main Node**: Orchestrates training, manages model updates, and coordinates workers
- **Worker Nodes**: Generate self-play games using the latest model
- **SSH Connectivity**: Secure communication between nodes

```
┌─────────────┐
│  Main Node  │
│  (Coach)    │
└─────┬───────┘
      │
      ├─── SSH ──► Worker 1 (Self-Play)
      ├─── SSH ──► Worker 2 (Self-Play)
      └─── SSH ──► Worker N (Self-Play)
```

## Setting Up Distributed Training

### 1. Configure Worker Nodes

Edit `configs/config.yaml` to add your worker nodes:

```yaml
distributed:
  enabled: true
  workers:
    - host: "worker1.example.com"
      user: "username"
      key_path: "~/.ssh/id_rsa"
      gpu_id: 0
    - host: "worker2.example.com"
      user: "username"
      key_path: "~/.ssh/id_rsa"
      gpu_id: 1
```

### 2. Prepare Worker Environments

On each worker node:
```bash
# Clone the repository
git clone https://github.com/yourusername/AZ-Go.git
cd AZ-Go

# Install dependencies
pip install -r requirements.txt

# Verify GPU availability
python -c "import torch; print(torch.cuda.is_available())"
```

### 3. SSH Key Setup

Ensure passwordless SSH access from main to workers:
```bash
# Generate SSH key if needed
ssh-keygen -t rsa -b 4096

# Copy to workers
ssh-copy-id username@worker1.example.com
```

### 4. Start Training

On the main node:
```bash
python start_main.py --distributed
```

## Worker Management

### Starting Workers

Workers are automatically started by the main node via SSH. The process:
1. Main node SSHs into worker
2. Starts `start_worker.py` with appropriate parameters
3. Worker begins self-play game generation
4. Results are sent back to main node

### Monitoring Workers

Check worker status:
```bash
# View all worker statuses
cat distributed/status.txt

# Monitor in real-time
watch -n 1 cat distributed/status.txt
```

### Worker Status Indicators

- **🟢 Active**: Worker is generating games
- **🟡 Syncing**: Worker is updating its model
- **🔴 Error**: Worker encountered an issue
- **⚪ Offline**: Worker is not connected

## Data Synchronization

### Model Distribution

1. Main node trains new model iteration
2. Model is serialized and compressed
3. Distributed to all workers via SCP
4. Workers load new model and resume self-play

### Game Collection

1. Workers generate self-play games
2. Games are batched (default: 100 games)
3. Compressed and sent to main node
4. Main node aggregates for training

## Performance Optimization

### Network Bandwidth

Minimize transfer overhead:
```yaml
distributed:
  compression: true  # Enable compression
  batch_size: 100   # Games per transfer
  sync_interval: 50 # Games between syncs
```

### GPU Utilization

Optimize worker GPU usage:
```yaml
self_play:
  games_per_worker: 1000
  parallel_games: 4  # Parallel MCTS instances
  batch_size: 8      # Neural net batch size
```

### Load Balancing

Distribute work evenly:
```python
# In configs/config.yaml
distributed:
  load_balancing: true
  worker_weights:
    worker1: 1.0  # Standard performance
    worker2: 2.0  # 2x faster machine
```

## Fault Tolerance

### Automatic Recovery

- Workers automatically reconnect after network issues
- Incomplete games are discarded
- Training continues with available workers

### Manual Intervention

Restart a specific worker:
```bash
# On main node
python distributed/ssh_connector.py --restart worker1
```

Remove a problematic worker:
```bash
# Edit config.yaml and remove worker
# Training will continue with remaining workers
```

## Monitoring and Debugging

### Logs

Check distributed training logs:
```bash
# Main node logs
tail -f logs/distributed_training.log

# Worker logs (on worker machine)
tail -f logs/worker_*.log
```

### Performance Metrics

Monitor training efficiency:
```python
# View in training output
Games/second: 145.2
Workers active: 4/4
Model sync time: 12.3s
Network usage: 45.6 MB/min
```

### Common Issues

**Worker won't connect:**
- Check SSH keys and permissions
- Verify network connectivity
- Ensure Python environment matches

**Slow game generation:**
- Check GPU utilization on workers
- Adjust parallel game settings
- Monitor network latency

**Model sync failures:**
- Verify disk space on workers
- Check file permissions
- Monitor network stability

## Best Practices

1. **Homogeneous Hardware**: Use similar GPUs across workers for balanced performance
2. **Local Network**: Keep workers on same network to minimize latency
3. **Regular Monitoring**: Check worker status frequently during long training runs
4. **Backup Models**: Regularly backup models in case of main node failure
5. **Resource Planning**: Ensure adequate CPU/RAM for parallel MCTS instances

## Scaling Guidelines

| Workers | Games/Hour | Training Time | Recommended Setup |
|---------|------------|---------------|-------------------|
| 1       | 500        | 48 hours      | Single GPU Dev    |
| 4       | 2,000      | 12 hours      | Small cluster     |
| 8       | 4,000      | 6 hours       | Medium cluster    |
| 16+     | 8,000+     | 3 hours       | Large cluster     |

## Advanced Configuration

### Custom Worker Scripts

Create specialized worker configurations:
```python
# custom_worker.py
from training.worker import Worker

class CustomWorker(Worker):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Custom initialization
```

### Dynamic Worker Addition

Add workers during training:
```python
from distributed.ssh_connector import SSHConnector

connector = SSHConnector()
connector.add_worker("new_worker.com", "username")
```