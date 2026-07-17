# AGENTS.md — Odyssey Attributional Semantics

## Project

**Attributional Semantics in English Translations of Homer’s Odyssey: Color, Character, and Hypergraphs**

## Isolation requirements

This project must remain under `/home/ubuntu/odyssey-attribution-computations` and must not modify, stop, restart, inspect secrets from, or reuse credentials belonging to `/home/ubuntu/claim-annotation` or `annotation.service`.

## Resource constraints

The cloud computer has limited memory and also runs another continuous workload. Run analyses sequentially, cap numeric-library threads at one, prefer sparse matrices and streamed files, and avoid loading large transformer models. Do not add swap, alter system services, open firewall ports, or install system packages without explicit user approval.

## Reproducibility

All source data must have checksums and provenance. Generated outputs belong under `outputs/`; processed data belong under `data/processed/`; temporary data belong under `data/interim/`. Scripts must be deterministic with fixed random seeds where relevant. Never commit credentials, caches, virtual environments, or protected copyrighted texts.

## Rights boundary

The repository may contain only the verified public-domain translation sources and the CC BY-SA 4.0 English timed text for *L’Odissea* (1911). Protected modern translations, screenplays, and unofficial subtitle texts must not be added.

## GitHub

The intended repository is private and uses the slug `odyssey-attributional-semantics`. GitHub authentication must be supplied through the authorized connector; do not copy tokens from unrelated files or services.
