"use client";
import { useCallback, useState } from "react";
import { verifyApi } from "../services/verifyApi";

export function useVerify() {
    const [stage, setStage] = useState("idle");
    const [error, setError] = useState(null);
    const [result, setResult] = useState(null);

    const reset = useCallback(() => {
        setStage("idle");
        setError(null);
        setResult(null);
    }, []);

    const verify = useCallback(async (file) => {
        setError(null);
        setResult(null);
        try {
            setStage("hashing");
            setStage("uploading");
            const res = await verifyApi.verify(file);
            setResult(res);
            setStage("done");
            return res;
        } catch (e) {
            setError(e.detail ?? e.message ?? "Verification failed");
            setStage("error");
            throw e;
        }
    }, []);

    return { stage, error, result, verify, reset };
}