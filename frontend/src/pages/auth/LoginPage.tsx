import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { KeyRound, ShieldCheck } from "lucide-react";
import { Button } from "@/components/common/Button";
import { Card } from "@/components/common/Card";
import { Input } from "@/components/common/Input";
import { Logo } from "@/components/layout/Logo";
import { InlineError } from "@/components/feedback/InlineError";
import { useAuth } from "@/hooks/useAuth";
import { ApiError } from "@/lib/api-client";

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const from = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname ?? "/dashboard";

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await login(form);
      navigate(from, { replace: true });
    } catch (caughtError) {
      setError(
        caughtError instanceof ApiError
          ? caughtError.message
          : "We could not sign you in right now.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="grid min-h-screen bg-health-grid lg:grid-cols-[1.15fr_0.85fr]">
      <section className="hidden px-8 py-10 lg:flex lg:flex-col lg:justify-between">
        <Logo />
        <div className="mx-auto max-w-xl">
          <span className="inline-flex items-center gap-2 rounded-full bg-white px-4 py-2 text-sm font-medium text-brand-700 shadow-soft">
            <ShieldCheck className="h-4 w-4" />
            Secure access to your MediGen workspace
          </span>
          <h1 className="mt-8 text-5xl font-semibold leading-tight text-slate-900">
            A calm frontend shell for your medication journey.
          </h1>
          <p className="mt-6 text-lg leading-8 text-slate-600">
            The backend is production-ready, and this foundation keeps auth, navigation,
            and future care workflows consistent from the very first screen.
          </p>
        </div>
        <div className="text-sm text-slate-500">
          Built for clean, responsive, healthcare-friendly experiences.
        </div>
      </section>

      <section className="flex items-center justify-center px-5 py-8 sm:px-8">
        <Card className="w-full max-w-md p-6 sm:p-8">
          <div className="lg:hidden">
            <Logo />
          </div>
          <p className="mt-6 text-xs font-semibold uppercase tracking-[0.24em] text-brand-600">
            Welcome back
          </p>
          <h2 className="mt-3 text-3xl font-semibold text-slate-900">Sign in to MediGen</h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Use the backend-authenticated account flow to enter the protected app shell.
          </p>

          <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
            <Input
              label="Email"
              type="email"
              autoComplete="email"
              placeholder="you@example.com"
              value={form.email}
              onChange={(event) =>
                setForm((current) => ({ ...current, email: event.target.value }))
              }
            />
            <Input
              label="Password"
              type="password"
              autoComplete="current-password"
              placeholder="Enter your password"
              value={form.password}
              onChange={(event) =>
                setForm((current) => ({ ...current, password: event.target.value }))
              }
            />

            {error ? <InlineError message={error} /> : null}

            <Button
              type="submit"
              size="lg"
              className="w-full"
              isLoading={isSubmitting}
              icon={<KeyRound className="h-4 w-4" />}
            >
              Sign in
            </Button>
          </form>

          <p className="mt-6 text-sm text-slate-600">
            New to MediGen?{" "}
            <Link className="font-semibold text-brand-700 hover:text-brand-800" to="/register">
              Create an account
            </Link>
          </p>
        </Card>
      </section>
    </div>
  );
}
