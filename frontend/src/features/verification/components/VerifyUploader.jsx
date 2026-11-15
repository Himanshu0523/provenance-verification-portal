"use client";
import { useRef, useState } from "react";
import { ShieldCheck } from "lucide-react";

export default function VerifyUploader({ onFile, disabled }) {
    const [drag, setDrag] = useState(false);
    const input = useRef(null);

    function pick(f) {
        if (f) onFile(f);
    }

  return (
        <div
        onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => {
            e.preventDefault();
            setDrag(false);
            pick(e.dataTransfer.files?.[0]);
        }}
        onClick={() => !disabled && input.current?.click()}
        className={`cursor-pointer rounded-2xl border-2 border-dashed p-10 text-center transition ${
            drag ? "border-slate-900 bg-slate-50" : "border-slate-300"
        } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
        >
        <ShieldCheck className="mx-auto mb-3" size={36} />
        <p className="font-medium">Drop a file to verify</p>
        <p className="text-sm text-slate-500">PNG, JPEG, or WebP up to 20 MB</p>
        <input
            ref={input}
            type="file"
            accept="image/png,image/jpeg,image/webp"
            hidden
            onChange={(e) => pick(e.target.files?.[0])}
        />
        </div>
    );
}