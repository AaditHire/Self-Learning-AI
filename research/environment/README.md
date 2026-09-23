# Phase 3B environment reconstruction record

`phase3b_host_pip_freeze.txt` is a snapshot of all 208 distributions currently
installed in the local Python 3.13.0 interpreter at the infrastructure
checkpoint. It was captured without installing or upgrading packages. The
Phase 3B raw training records independently recorded Windows 11
`10.0.26200`, Python 3.13.0, PyTorch `2.9.0+cu130`, Transformers 4.57.1,
bitsandbytes 0.50.2, PEFT 0.17.1, CUDA runtime 13.0, and an RTX 3060 Laptop
GPU. This host currently reports NVIDIA driver 610.74 and 6144 MiB VRAM.

The current snapshot additionally pins Accelerate 1.15.0, tokenizers 0.22.1,
pytest 9.1.1, NumPy 2.2.6, SciPy 1.16.2, safetensors 0.6.2, and psutil
7.1.2. The JDK used by the frozen GOCO evaluation path is local Eclipse
Temurin 25.0.1+8 (`.tools/jdk-25.0.1+8`); the deterministic compiler JAR
SHA-256 is `42478b3500ff31df65f411e4072f578be5fede844020392a664eb89865b2a2fb`.

The current package snapshot is **not proven to be the exact full package set
at Phase 3B execution**. The raw training records did not capture every
transitive package, wheel hash, OS patch level, CUDA driver component, or JDK
binary hash. `pip freeze` pins versions but not wheel identities or index
availability. Reproduction should use the frozen config, local model shard
hashes, adapter hashes, compiler hash, and raw run environment fields, and
report any unavailable component instead of substituting silently.
