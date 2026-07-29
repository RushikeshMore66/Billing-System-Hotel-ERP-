"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { authApi } from "@/services/api";
import { useAuth } from "@/providers/AuthProvider";
import { Building2, Loader2, Lock, Mail } from "lucide-react";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const { login, user, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && user) {
      router.push("/dashboard");
    }
  }, [user, isLoading, router]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await authApi.login({ email, password });
      await login(res.data);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Invalid credentials");
    } finally {
      setLoading(false);
    }
  };

  if (isLoading || user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg">
        <Loader2 size={32} className="animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 ndl-card p-8">
        <div className="flex flex-col items-center">
          <div
            className="flex items-center justify-center rounded-2xl shrink-0 mb-6"
            style={{
              width: 64,
              height: 64,
              background: "linear-gradient(135deg, #155E4B 0%, #1a7a61 100%)",
              boxShadow: "0 4px 12px rgba(21,94,75,0.3)",
            }}
          >
            <Building2 size={32} className="text-white" />
          </div>
          <h2 className="text-center text-3xl font-extrabold text-text-primary tracking-tight">
            NiralayOS
          </h2>
          <p className="mt-2 text-center text-sm text-text-secondary">
            Sign in to access your dashboard
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleLogin}>
          {error && (
            <div className="p-3 text-sm text-danger bg-danger-50 rounded-lg border border-danger-100 flex items-center justify-center text-center">
              {error}
            </div>
          )}
          <div className="space-y-4">
            <div>
              <label className="ndl-label block mb-1.5" htmlFor="email">
                Email Address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail size={18} className="text-text-secondary opacity-60" />
                </div>
                <input
                  id="email"
                  type="email"
                  required
                  className="ndl-input pl-10"
                  placeholder="admin@niralayos.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
            </div>
            <div>
              <label className="ndl-label block mb-1.5" htmlFor="password">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock size={18} className="text-text-secondary opacity-60" />
                </div>
                <input
                  id="password"
                  type="password"
                  required
                  className="ndl-input pl-10"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="ndl-btn-primary w-full py-3 text-sm flex justify-center"
            >
              {loading ? <Loader2 size={18} className="animate-spin" /> : "Sign in"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
