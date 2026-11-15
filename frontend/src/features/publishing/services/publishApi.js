import { apiClient } from "@/lib/api/client";

export const publishApi = {
    publish: (formData) =>
        apiClient
        .post("/publish", formData, {
            headers: { "Content-Type": "multipart/form-data" },
        })
        .then((r) => r.data),
};