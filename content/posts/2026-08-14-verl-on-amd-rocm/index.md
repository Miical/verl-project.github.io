---
title: "verl on AMD: production-ready RL post-training on ROCm"
date: 2026-08-14
authors:
  - "Fuwei Yang"
  - "Zhaodong Bing"
  - "Mingjie Lu"
  - "Xiaohong Kou"
  - "Yuhan Yang"
  - "Wei Cai"
  - "Liz Li"
  - "Yuankai Chen"
  - "Yao Fu"
  - "Dong Li"
  - "Zhenyu Gu"
summary: "RL post-training on AMD Instinct GPUs is here: a turnkey ROCm container, AITER-accelerated vLLM and SGLang rollout, and accuracy validated on both MI300 and MI350 series."
tags:
  - amd
  - rocm
  - performance
  - vllm
  - sglang
  - megatron
  - fsdp
image: "cover.png"
math: false
toc: true
---

Reinforcement learning post-training on AMD Instinct GPUs is here — with a
turnkey container, AITER-accelerated vLLM and SGLang rollout, and accuracy
validated on both MI300 and MI350 series.

[verl](https://github.com/verl-project/verl) — the open-source implementation of
the RL controller — has quickly become one of the most widely adopted RL
post-training frameworks, powering PPO, GRPO and DAPO pipelines with a flexible
mix of rollout and training engines. Today, that same power runs on AMD Instinct
GPUs. Whether you're on MI300 or the latest MI350 series, you can stand up verl
on ROCm in minutes, scale it across your rollout and training engines, and trust
the numbers. Here's what makes AMD a first-class home for verl.

## Zero-friction setup: one container, no dependency headaches

Getting a modern RL stack running usually means fighting a maze of dependencies
— matching CUDA/ROCm versions, building attention kernels from source, and
praying the wheels line up. On AMD, that pain is gone.

AMD ships a turnkey ROCm container, `verlai/verl:rocm7.14_torch2.12_release_0724`,
built from [`docker/rocm/Dockerfile.rocm`](https://github.com/verl-project/verl/blob/main/docker/rocm/Dockerfile.rocm),
so you can go from zero to training without hand-assembling a single dependency.
The image bundles the entire runtime stack — ROCm, PyTorch, Triton, vLLM,
SGLang, AITER, TransformerEngine and Megatron-core — all pinned to a set of
versions verified to work together. Pull it, mount your data, and run: RL
post-training on AMD is a `docker run` away, so you can spend your time on
reward design and experiments rather than on environment setup.

- **No dependency installation.** Everything RL post-training needs is baked in
  — no extra source builds, no extra version detective work. There's an
  [end-to-end AMD tutorial](https://verl.readthedocs.io/en/latest/amd_tutorial/amd_quick_start.html)
  covering build, run, and example PPO/GRPO commands.
- **Built for multiple architectures.** The image targets `gfx942` (MI300 series
  — MI300X / MI308X / MI325X) and `gfx950` (MI350 series — MI350X /
  MI355X) out of the box.
- **Customizable for your setup.** Teams that want to tailor the image can do so
  — target a specific GPU architecture, pin component versions, and tune the
  build to their environment — all documented in the
  [AMD support section of the verl README](https://github.com/verl-project/verl/tree/main#amd-support-rocm-kernel).

This is all backed by CI on real AMD hardware: end-to-end tests now run on a
community-hosted runner, so changes to the verl repository are validated on AMD
hardware before merge. Coverage is a work in progress and actively expanding
toward parity with the other platforms.

## Two rollout backends — vLLM and SGLang, both AITER-accelerated

Rollout is the key component of RL post-training, and on AMD you're not locked
into a single engine: verl supports both vLLM and SGLang on ROCm. Both are
accelerated by [AITER](https://github.com/ROCm/aiter), AMD's AI Tensor Engine
for ROCm kernel library — powering attention, RMSNorm / RoPE, mixture-of-experts
(MoE), and quantization — with everything fully overridable if you want to
experiment.

- **vLLM** — the default, battle-tested rollout engine; enable the AITER path
  with a few environment variables.
- **SGLang** — a first-class alternative that runs on ROCm with AITER kernels
  enabled by default.

Both engines work across both of verl's integration modes — colocated (rollout
and training share GPUs with fast weight transfer) and fully async (rollout and
training run concurrently for maximum GPU utilization, with live parameter sync
back to the rollout workers). Whichever engine and mode fit your workload,
AMD-accelerated rollout is ready to go.

## Validated accuracy — MI300 and MI350 series, colocated and fully-async

Enablement is only half the story. What ultimately matters is whether the model
you train on AMD is as good as the model you'd train anywhere else. It is — and
we've measured it.

Training accuracy has been validated on both AMD MI300 and MI350 series, across
both colocated and fully-async modes. RL post-training on Instinct GPUs converges
to the quality you expect, so you can move real workloads onto AMD with
confidence rather than crossing your fingers.

The MI350-series runs below were measured on MI350. MI350X and MI355X are the
same `gfx950` silicon and differ in board power and cooling rather than in
numerics, so the accuracy results carry over between them unchanged — only
throughput tracks the power envelope.

### Case study: Qwen3-8B GRPO with SGLang rollout on MI350

Start with the SGLang rollout backend — the first-class alternative to vLLM
introduced above — to show it delivers the same accuracy on AMD. Key run
parameters:

| Parameter | Value |
| --- | --- |
| Algorithm | GRPO (`use_kl_loss=True`, `kl_loss_coef=0.001`) |
| Training backend | FSDP (PyTorch Fully Sharded Data Parallel) |
| Rollout engine | SGLang async rollout server, AITER-accelerated, group size n = 5 |
| Task | GSM8K + MATH (train and validate on both) |
| Max prompt / response length | 1,024 / 2,048 tokens |
| Train batch / PPO mini-batch | 1,024 / 256 |
| Learning rate | 1e-6 |
| Execution mode | Colocated, single node — 8 GPUs |

Note that "async" here refers to SGLang's async rollout server, which serves
generation requests concurrently within a rollout step. It is not verl's
fully-async execution mode: rollout and training still share the same 8 GPUs and
alternate, which is what "colocated" in the table means. The fully-async mode,
where rollout and training run on disjoint GPUs at the same time, is covered in
the next two case studies.

The training curves show textbook convergence:

{{< figure src="qwen3_8b.jpg" alt="Four panels over 200 training steps: GSM8K and MATH validation accuracy, mean training reward, rollout-to-actor KL, and wall-clock time per step" caption="Qwen3-8B GRPO on GSM8K and MATH. SGLang async rollout server with AITER, FSDP trainer, colocated on 8xMI350." >}}

1. **Strong accuracy on both benchmarks.** GSM8K validation accuracy climbs from
   0.82 to ~0.955 (peak 0.956) within the first ~30 steps and holds there, while
   the harder MATH benchmark rises steadily from 0.37 to ~0.835 (peak 0.839).
   Mean training reward tracks them in lockstep, from 0.62 to ~0.90 — no
   reward-hacking, no collapse. An 8B model reaching ~95% on GSM8K and ~84% on
   MATH is exactly the quality bar you'd expect from a well-behaved GRPO run.
2. **SGLang and the FSDP trainer stay numerically locked.** The rollout↔actor
   mismatch is negligible: `actor/ppo_kl` hovers around 1e-4 during the entire
   run. In other words, the tokens that the AITER-accelerated SGLang samples
   during rollout are assigned essentially identical probabilities when the FSDP
   actor recomputes them.

### Case study: Qwen2.5-Math-7B DAPO, fully-async on MI300

We reproduced verl's fully-async experiments on AMD MI300: DAPO post-training of
Qwen2.5-Math-7B on the MATH task. Key parameters are defined as follows:

| Parameter | Value |
| --- | --- |
| Rollout engine | vLLM, AITER enabled, group size n = 16 |
| Training backend | FSDP2 |
| Max prompt / response length | 2,048 / 28,672 (28k) tokens |
| PPO mini-batch size | 32 |
| Learning rate | 1e-6 |
| Execution mode | Fully-async — 16 rollout GPUs + 16 training GPUs (32 total) |
| `staleness_threshold` | 0.5 |
| `trigger_parameter_sync_step` | 4 |
| `partial_rollout` | True |

The training curves tell the story:

{{< figure src="qwen2.5_7b.jpg" alt="Four panels over 400 logged steps: MATH validation accuracy, mean training reward, wall-clock time per step, and rollout-to-actor KL" caption="Qwen2.5-Math-7B DAPO on MATH. vLLM with AITER, FSDP2 trainer, fully-async on 32 MI300 GPUs (16 rollout + 16 training)." >}}

1. **Convergence is clean, and the final score matches the reference.**
   Validation accuracy climbs from 0.13 to a peak of 0.34 and holds around 0.32,
   while mean training reward rises from −0.98 to +0.17 in lockstep — no
   reward-hacking, no collapse. Critically, these numbers land right on top of
   verl's published reference for the same configuration
   (`staleness_threshold = 0.5`, partial rollout): the upstream
   [fully-async-policy results](https://github.com/verl-project/verl/tree/main/verl/experimental/fully_async_policy#experiments)
   report max accuracy 0.3302 for the same 16+16 GPU allocation on H20, while on
   AMD we reproduce the result with the same training settings and measure 0.34.
2. **The KL curve confirms stable off-policy training.** Rollout↔actor KL
   (`actor/ppo_kl`) sits at ~0.0007 for the first ~100 logged steps, then rises
   and settles onto a controlled 0.15–0.25 plateau once staleness kicks in. The
   run is stable end to end, with no explosive divergence despite training on
   deliberately stale samples.
3. **Fully-async is dramatically faster per training step.** Against a colocated
   DAPO run of the same model on the same 32 GPUs, we compare wall-clock time
   per training step over the first 64 steps:

| | Fully-async | Colocated |
| --- | --- | --- |
| Step time (median) | ~219 s | ~394 s |
| Step time (mean) | ~249 s | ~400 s |
| Speed-up per step | ~1.8× | 1.0× (baseline) |

A training step of fully-async is ~1.8× faster than the colocated baseline. In
this experiment we verified on the AMD platform that fully-async mode achieves
the expected accuracy and performance speedup that were originally reported on
H20.

{{< note type="info" title="One honest caveat" >}}
In the step-time panel above, per-step time is flat at ~190–200 s for the first
~260 steps, then climbs into the 600–1,200 s range toward the end of training. This isn't a regression or
instability — it's the expected response-length growth of reasoning RL: as model
capacity saturates, the model only learns to increase the response length
without improving accuracy. We observe its average response roughly double
(from ~890 to ~1,850 tokens) during the late stage of the experiment. The same
pattern shows up in the reported H20 experiment data.
{{< /note >}}

### Case study: Qwen3.5-35B-A3B MoE on MI350

Now a more complex case: GRPO post-training of Qwen3.5-35B-A3B on the
geometry3k reasoning task on MI350, with the Megatron backend, validated in both
colocated and fully-async modes.

| | Colocated | Fully-async |
| --- | --- | --- |
| Rollout / training placement | Shared 8 GPUs | 4 GPUs rollout + 4 GPUs training |
| Megatron parallelism | TP 2, expert-parallel 8 | TP 2, expert-parallel 4 |
| Async knobs | N/A | `staleness_threshold=0.5`, sync every 4 steps |
| Rollout engine | vLLM + AITER, group size n = 5 | vLLM + AITER, group size n = 5 |
| Max response length | 2,048 tokens | 2,048 tokens |

Both modes deliver clean, stable convergence:

{{< figure src="qwen3.5_35b_a3b.jpg" alt="Four panels comparing colocated and fully-async over 150 training steps: geometry3k validation accuracy, mean training reward, rollout-to-actor KL, and per-GPU throughput" caption="Qwen3.5-35B-A3B GRPO on geometry3k. vLLM with AITER, Megatron backend, 8xMI350, colocated versus fully-async." >}}

- **Validation accuracy climbs steadily.** Both modes rise from a ~0.37–0.48
  start to a peak of ~0.77–0.78 within the first ~75 steps and hold there.
- **Training reward rises in lockstep**, from ~0.34 to ~0.82 in both modes,
  tracking the validation gains rather than reward-hacking.
- **Rollout↔actor KL stays tiny** — ≈0.001 for fully-async and ≈0 for colocated
  — meaning the AITER-accelerated vLLM rollout and the Megatron training policy
  stay numerically almost identical.
- **Fully-async sustains ~310 tok/s/GPU versus colocated's ~216** — roughly 1.4×
  higher per-GPU throughput. That's exactly the payoff of decoupling.

So a 35B-parameter MoE model trained end-to-end with GRPO on AMD MI350 converges
smoothly to strong accuracy in both colocated and fully-async modes.

## The bottom line

RL post-training on AMD Instinct is production-ready:

1. **Effortless setup** — a turnkey ROCm container with the full stack baked in,
   so there are no dependencies to wrangle, and end-to-end CI on real MI300
   hardware keeping it solid (with coverage still expanding).
2. **Two rollout backends** — both vLLM and SGLang, AITER-accelerated out of the
   box, in both colocated and fully-async modes.
3. **Validated accuracy** — confirmed on MI300 and MI350 series, in both execution
   modes, with AITER-accelerated rollout delivering speed without sacrificing
   convergence.

Looking ahead, AMD will continue working closely with the verl community to
support emerging models and capabilities, including architectures such as
DeepSeek-V4, agentic RL workloads, and integration with platforms such as
VeOmni. We will also improve rollout efficiency through technologies such as
speculative decoding and FP4 inference.

Our goal is simple: make the latest verl models and features work out of the box
on AMD Instinct GPUs, with strong performance, validated accuracy, and a
reliable experience for customers.
