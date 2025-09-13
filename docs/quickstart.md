# Quickstart

This document describes the minimal workflow for using the cognitive core.

## Metrics

Run metric evaluation over a task file:

```
cogctl metrics run --tasks benchmarks/golden12/tasks.jsonl \
                   --rubric config/rubrics/umaa_epaup_v1.yaml \
                   --out runs/latest.jsonl
```

## ISR Simulation

```
cogctl isr simulate --network data/demo/isr_networks/ring_32.edgelist \
                     --K 1.5 --tmax 50 --dt 0.01 --out runs/isr_ring32.npz
```
