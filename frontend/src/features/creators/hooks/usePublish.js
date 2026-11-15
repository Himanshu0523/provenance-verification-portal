"use client";
import { useState, useCallback } from "react";
import { loadKey } from "@/lib/crypto/keyStorage";
import { signText } from "@/lib/crypto/webCrypto";
import { buildCanonicalPayload } from "@/lib/crypto/canonical";
import { sha256HexOfFile, inferMime } from "@/lib/crypto/fileHash";
import { publishApi } from "../services/publishApi";

export function usePublish(creatorId) {
    const [stage, setStage] = useState("idle");
    const [progress, setProgress] = useState(0);
    const [error, setError] = useState(null);
    const [result, setResult] = useState(null);

    const reset = useCallback(() => {
        setStage("idle");
        setProgress(0);
        setError(null);
        setResult(null);
    }, []);

    const publish = useCallback(async (file) => {
        setError(null);
        setResult(null);
        try {
            if (!creatorId) throw new Error("Register a creator first (Settings).");
            const stored = await loadKey(creatorId);
            if (!stored) throw new Error("No local private key. Generate one in Settings.");

            setStage("hashing");
            const sha256 = await sha256HexOfFile(file);

            setStage("signing");
            const mime = inferMime(file);
            if (!mime) throw new Error("Unsupported file type.");
            const clientCreatedAt = new Date()
                .toISOString()
                .replace(/\.\d{3}Z$/, "Z");

            const canonical = buildCanonicalPayload({
                asset_sha256: sha256,
                client_created_at: clientCreatedAt,
                creator_id: creatorId,
                file_size: file.size,
                key_id: stored.backendKeyId,
                mime_type: mime,
                original_filename: file.name,
            });
            const signature = await signText(stored.privateKeyHex, canonical);

            setStage("uploading");
            const form = new FormData();
            
            form.append("file", file);
            form.append("creator_id", creatorId);
            form.append("key_id", stored.backendKeyId);
            form.append("client_created_at", clientCreatedAt);
            form.append("signature", signature);

            const res = await publishApi.publish(form);

            if (res.canonical_payload !== canonical) {
                    console.warn("Canonical payload mismatch", {
                    local: canonical, server: res.canonical_payload,
                });
            }
            setResult(res);
            setStage("done");
            return res;
        } catch (e) {
            setError(e.detail ?? e.message ?? "Publish failed");
            setStage("error");
            throw e;
        }
    }, [creatorId]);

    return { stage, progress, setProgress, error, result, publish, reset };
    }