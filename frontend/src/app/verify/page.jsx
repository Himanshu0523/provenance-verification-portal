"use client";
import { useState } from "react";
import { useVerify } from "@/features/verification/hooks/useVerify";
import VerifyUploader from "@/features/verification/components/VerifyUploader";
import VerificationResult from "@/features/verification/components/VerificationResult";

export default function VerifyPage() {
  const { verify, stage, error, result, reset } = useVerify();
  const [busyFile, setBusyFile] = useState(null);

  const busy = stage === "hashing" || stage === "uploading";

  async function handleFile(file) {
    setBusyFile(file);
    try {
      await verify(file);
    } catch {
      /* error already captured in hook */
    }
  }

  return (
    <main className="mx-auto max-w-3xl space-y-4 p-6">
      <h1 className="text-2xl font-bold">Verification Portal</h1>
      <p className="text-sm text-slate-600">
        Upload a file to check whether it matches a published asset exactly, and
        whether the recorded signature is still valid.
      </p>

      {!result && (
        <VerifyUploader onFile={handleFile} disabled={busy} />
      )}

      {busy && (
        <p className="text-sm text-slate-600">
          Verifying <span className="font-mono">{busyFile?.name}</span>…
        </p>
      )}
      {stage === "error" && error && (
        <p className="text-sm text-red-600">{error}</p>
      )}

      {result && <VerificationResult result={result} onReset={reset} />}
    </main>
  );
}