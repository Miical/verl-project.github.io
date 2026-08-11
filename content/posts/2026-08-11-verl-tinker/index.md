---
title: "Introducing verl-tinker: Your Tinker loop, your GPUs"
date: 2026-08-11
authors:
  - "Tianle Zhong*"
  - "Huaye Zeng*"
  - "Xibin Wu"
  - "Siping Tao"
  - "Peng Wu"
  - "Yifan Pi"
  - "Xiao Yu"
summary: "Keep the Tinker Cookbook loop you know, and run SFT, RL, and distillation on verl-managed GPU workers you control."
image: "verl_tinker_logo.png"
tags:
  - training
  - rollout
  - recipes
  - distillation
math: false
toc: true
---

What if you could keep a Tinker Cookbook training loop exactly where it is,
but run the heavy lifting on your own GPUs?

That is what `verl-tinker` makes possible. Point an existing Tinker or Tinker
Cookbook program at a local HTTP endpoint and it can drive supervised fine
tuning (SFT), reinforcement learning (RL), online and offline distillation,
checkpointing, and rollout on verl-managed workers. The client does not need
to know about Ray, vLLM, VeXact, or even verl itself.

In other words: **the experiment loop stays simple; the infrastructure becomes
yours.**

The implementation is available now in the
[`verl_tinker` recipe](https://github.com/verl-project/verl-recipe/tree/main/verl_tinker).
It is a Tinker-compatible server backed by Ray Serve, FastAPI, verl workers,
and vLLM or VeXact rollout engines.

## Keep the loop. Bring the infrastructure.

Tinker Cookbook recipes describe an algorithm from the researcher's point of
view. They build data, ask a model to sample or compute log probabilities,
submit a loss-bearing batch, and take an optimizer step. It is an appealingly
compact way to express an experiment.

verl tackles the other side of the problem: distributed actor, reference,
rollout, and teacher workers; model-state movement; parallelism; offload; and
checkpoint storage.

`verl-tinker` joins those two worlds at the API boundary. Researchers keep the
concise Cookbook loop and choose the cluster, model weights, inference engine,
parallelism strategy, and storage behind it. The client environment needs only
`tinker` and `tinker-cookbook`; the server owns the distributed runtime.

This is more than a convenience wrapper. Tinker and verl disagree—in useful
ways—about data layouts, concurrency, and model identity. Bridging them means
making those differences invisible to the training loop without making them
ambiguous to the server.

## Start a workload in minutes

Install the server environment from the root of `verl-recipe`, then start an
actor-and-rollout configuration:

```bash
./install_verl.sh --recipe verl_tinker
cd verl_tinker
python -m verl_tinker.start \
  --config configs/quick_start/actor_rollout.yaml
```

Once `GET /api/v1/healthz` returns `{"status":"ready"}`, point a client at the
server:

```bash
export TINKER_BASE_URL=http://127.0.0.1:8000/
export TINKER_API_KEY=tml-verl-tinker-local

cd verl_tinker/client_examples
uv sync
uv run run_single_test.py \
  --test-name sft_tulu3
```

That is the whole handoff. The Cookbook recipe issues familiar Tinker calls;
the server turns them into distributed verl work.

The bundled [client examples](https://github.com/verl-project/verl-recipe/tree/main/verl_tinker/client_examples)
are intentionally lightweight wrappers around recipes from the
[Tinker Cookbook](https://github.com/thinking-machines-lab/tinker-cookbook).
They demonstrate how to connect familiar workloads—including SFT, supervised
distillation, GSM8K RL, SFT followed by RL, and single- or multi-teacher
on-policy distillation—to a `verl-tinker` server.

They are examples, not a required client layer. Because `verl-tinker` speaks
the Tinker API, you can point your own program built with the Tinker SDK at the
same endpoint and run your own data, training loop, and workflow.

Three quick-start configurations cover the common shapes:

- `actor.yaml` for SFT and optimizer-only workflows;
- `actor_rollout.yaml` when the client calls `asample`;
- `actor_rollout_ref.yaml` for RL that requests reference log probabilities for KL penalties.


## What happens after the HTTP call?

A request passes through four layers:

```text
Tinker / Tinker Cookbook client
              |
              | Tinker-compatible HTTP
              v
FastAPI routes on one Ray Serve deployment
              |
              | request scheduling and state checks
              v
Tinker operations and datum translation
              |
              | verl TensorDict / generation request
              v
verl actor + optional rollout, reference, and teacher workers
```


## Bring your teachers, too

Distillation is where this bridge gets especially interesting. A Tinker
program can use one or more larger, frozen models as teachers, ask them to
generate or return top-K log probabilities, and use those signals to train a
smaller actor—all through the same familiar client API.

That means you can explore single-teacher or multi-teacher on-policy
distillation without building a separate serving stack for every model. Your
training loop decides how to use each teacher; `verl-tinker` runs the actor and
teachers on the GPU resources you assign to them.

The recipe includes two ready-to-adapt starting points:

- The [single-teacher config](https://github.com/verl-project/verl-recipe/blob/main/verl_tinker/configs/advance/qwen3_1b7_actor_qwen3_30b_a3b_teacher.yaml)
  pairs a Qwen3-1.7B actor with a Qwen3-30B-A3B teacher on eight GPUs.
- The [multi-teacher config](https://github.com/verl-project/verl-recipe/blob/main/verl_tinker/configs/advance/qwen3_8b_actor_qwen3_32b_qwen3_235b_teachers.yaml)
  shows a Qwen3-8B actor learning from Qwen3-32B and Qwen3-235B-A22B teachers
  across two eight-GPU nodes.

Use these configs as templates: swap in your models, choose the parallelism
that fits your cluster, and let your Tinker code decide what each teacher
contributes to the learning signal.

## Where the boundary is today

For most workflows, `verl-tinker` lines up closely with Tinker. The main
difference is that a server currently manages one trainable model and one
rollout replica.

Because that rollout is shared, a sampling session created from the trainable
model is tied to a particular version of its weights. If the rollout is later
synchronized to newer weights—or otherwise diverges from the version that
session expects—the earlier sampling resource may no longer be available.
Teacher sampling and reference-log-probability requests are separate and are
not affected by this restriction.

You will not silently sample from the wrong weights. `verl-tinker` keeps track
of which model version each sampling resource belongs to and tells you when a
resource is no longer available.

Within that boundary, the division of labor stays simple: **your Tinker code
owns the experiment; verl owns distributed execution.** You keep the loop you
want, while choosing the GPUs, rollout engine, placement, offload, and
checkpoints underneath it.

If that sounds like the missing bridge in your workflow, start with the
[`verl_tinker` recipe](https://github.com/verl-project/verl-recipe/tree/main/verl_tinker)
and run one of the included client examples.

`verl-tinker` was developed by the ByteDance AML/Seed Team.
