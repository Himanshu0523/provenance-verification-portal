"use client";

import { useCallback, useEffect, useState } from "react";
import { creatorApi } from "../services/creatorApi";

const CREATOR_ID_KEY = "provenance.creatorId";

export function useCreator() {
    const [creator, setCreator] = useState(null);
    const [keys, setKeys] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const refresh = useCallback(async (id) => {
        const creatorId = id ?? localStorage.getItem(CREATOR_ID_KEY);
        if (!creatorId) return;
        
        setLoading(true);
        setError(null);
        try {
        const [c, k] = await Promise.all([
            creatorApi.get(creatorId),
            creatorApi.listKeys(creatorId),
        ]);
        setCreator(c);
        setKeys(k);
        } catch (e) {
        localStorage.removeItem(CREATOR_ID_KEY);
        setCreator(null);
        setKeys([]);
        setError(e.detail ?? "Failed to load creator");
        } finally {
        setLoading(false);
        }
    }, []);

  // Fetch on mount safely using an async IIFE inside useEffect 
  // or tracking initial load to satisfy the lint rule cleanly
    useEffect(() => {
        const creatorId = localStorage.getItem(CREATOR_ID_KEY);
        if (creatorId) {
        refresh(creatorId);
        }
    }, [refresh]);

    const register = useCallback(async (displayName, email) => {
        setLoading(true);
        setError(null);
        try {
        const c = await creatorApi.register({
            display_name: displayName,
            email: email || null,
        });
        localStorage.setItem(CREATOR_ID_KEY, c.id);
        setCreator(c);
        setKeys([]);
        return c;
        } catch (e) {
        setError(e.detail ?? "Registration failed");
        throw e;
        } finally {
        setLoading(false);
        }
    }, []);

    return { creator, keys, loading, error, register, refresh };
}