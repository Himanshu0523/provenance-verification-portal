import { apiClient } from "@/lib/api/client";

export const creatorApi = {
    register: (body) => apiClient.post("/creators", body).then((r) => r.data),
    get: (id) => apiClient.get(`/creators/${id}`).then((r) => r.data),
    registerKey: (id, body) => apiClient.post(`/creators/${id}/keys`, body).then((r) => r.data),
    listKeys: (id) => apiClient.get(`/creators/${id}/keys`).then((r) => r.data),
    revokeKey: (id, keyId) => apiClient.post(`/creators/${id}/keys/${keyId}/revoke`).then((r) => r.data),
    verifySignature: (id, body) => apiClient.post(`/creators/${id}/verify-signature`, body).then((r) => r.data),
};