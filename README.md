# Deepfake & AI Provenance Verification Portal

## Cross-Platform Cryptographic Signing & Vector-Based Forensic Lineage Engine

---

## 📌 Project Objective

The objective of this project is to build a **tamper-evident, end-to-end chain of custody for digital media** that proves content authenticity at creation and survives real-world social media distribution.

While traditional provenance tools break the moment platforms like WhatsApp, Instagram, or X strip file metadata and re-encode pixels, this portal bridges **Applied Cryptography** and **Multimodal Vector Search** to keep media verifiable anywhere online:

### 1. Cryptographic Origin Signing
* Enables journalists and creators to sign raw images and videos at upload using client-side **SHA-256** hashing, **Ed25519** asymmetric signatures, and **C2PA-style JSON manifests** logged in an immutable PostgreSQL audit trail.

### 2. Survivable Vector Recovery (`pgvector` + CLIP)
* Defeats metadata stripping and heavy compression by indexing **512-dimensional visual frame embeddings** alongside perceptual hashes (`pHash`), allowing viewers to trace cropped or screenshotted reposts back to the original signed source.

### 3. Visual Edit Lineage & Pixel Forensics
* Models derivative edits as a **Directed Acyclic Graph (DAG)** and generates OpenCV **Structural Similarity (SSIM)** pixel-difference heatmaps—empowering audiences to visually distinguish harmless edits (crops, color grading) from malicious deepfake manipulation.

### 4. Pre-Sign Synthetic Guardrail
* Screens incoming media with a lightweight deepfake artifact detector prior to signing to prevent bad actors from certifying pre-existing AI-generated content.

### 5. Zero-Trust Public Verification API
* Delivers a sub-second verification portal and REST API where
