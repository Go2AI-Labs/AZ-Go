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
- **Main Node (Overseer)**: Orchestrates training, manages model updates, and coordinates workers
- **Worker Nodes**: Generate self-play games and arena matches using the latest models
- **SSH Connectivity**: Workers connect to main node to download models and upload results
- **Status-based Coordination**: Main node announces training phase via status.txt file

```
┌─────────────┐
│  Main Node  │
│  (Overseer) │
└─────┬───────┘
      │
      ├─── Status File ──► Worker 1 (Self-Play/Arena)
      ├─── Status File ──► Worker 2 (Self-Play/Arena) 
      └─── Status File ──► Worker N (Self-Play/Arena)
```

Note: Workers poll the main node's status file to determine current training phase.

## Setting Up Distributed Training

### 1. Configure Settings

**Main Node Configuration:**

Create `configs/sensitive.yaml` with main node details:
```yaml
main_server_address: "main.example.com"  # Address workers will connect to
main_username: "username"                # SSH username on main node
main_directory: "/path/to/AZ-Go"        # Absolute path to AZ-Go on main
```

**Enable Distributed Training:**

In `configs/config.yaml`, set:
```yaml
enable_distributed_training: true
num_games_per_distributed_batch: 1      # Games before uploading to main
num_parallel_games: 12                  # Parallel games per worker
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

**On the main node:**
```bash
python start_main.py
```

**On each worker node:**
```bash
python start_worker.py
```

Note: The `--distributed` flag is not used. Distributed mode is controlled by the `enable_distributed_training` setting in config.yaml.

## Worker Management

### Starting Workers

Workers must be manually started on each worker node. The process:
1. SSH into each worker machine
2. Navigate to the AZ-Go directory
3. Run `python start_worker.py`
4. Worker connects to main node and begins polling for status
5. Worker automatically switches between self-play and arena modes based on main node status

### Monitoring Training Status

Check current training phase:
```bash
# View current training status
cat distributed/status.txt
```

Possible status values:
- **self_play**: Workers should generate self-play games
- **neural_net_training**: Main node is training the neural network
- **arena**: Workers should run arena matches between models

Note: The status.txt file indicates the current training phase, not individual worker statuses.

## Data Synchronization

### Model Distribution

1. Main node saves models to `logs/checkpoints/`:
   - `best.pth.tar`: Current best model for self-play
   - `current_net.pth.tar`: New model for arena evaluation
   - `previous_net.pth.tar`: Previous model for arena comparison
2. Workers download models via SSH when needed
3. Workers automatically check for new models based on training phase

### Game Collection

1. Workers generate games based on current status
2. Self-play examples uploaded to `distributed/self_play/`
3. Arena outcomes uploaded to `distributed/arena/`
4. Main node polls directories and aggregates results
5. Batch size controlled by `num_games_per_distributed_batch` setting

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
# SSH into the worker machine
# Kill the existing process if running
# Then restart:
python start_worker.py
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

### Implementation Details

**Key Classes:**
- `Overseer` (training/overseer.py:14): Main node coordinator
- `Worker` (training/worker.py): Worker node implementation  
- `SSHConnector` (distributed/ssh_connector.py:12): Handles file transfers
- `StatusManager` (distributed/status_manager.py:15): Manages training phase status

**Training Phases:**
1. **Self-Play Phase**: Workers generate training games
2. **Neural Net Training**: Main node trains new model (workers idle)
3. **Arena Phase**: Workers evaluate new vs previous model

The main node cycles through these phases automatically for each iteration.