import { apiClient } from "@/lib/api/client";

export const verifyApi = {
    verify: (file) => {
        const form = new FormData();
        form.append("file", file);
        return apiClient
        .post("/verify", form, {
            headers: { "Content-Type": "multipart/form-data" },
        })
        .then((r) => r.data);
    },
};