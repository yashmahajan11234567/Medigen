import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { UserPlus } from "lucide-react";
import { Button } from "@/components/common/Button";
import { Card } from "@/components/common/Card";
import { Input } from "@/components/common/Input";
import { InlineError } from "@/components/feedback/InlineError";
import { Logo } from "@/components/layout/Logo";
import { useAuth } from "@/hooks/useAuth";
import { ApiError } from "@/lib/api-client";

export function RegisterPage() {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    password: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await register(form);
      navigate("/dashboard", { replace: true });
    } catch (caughtError) {
      setError(
        caughtError instanceof ApiError
          ? caughtError.message
          : "We could not create your account right now.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-health-grid px-5 py-8 sm:px-8">
      <Card className="w-full max-w-5xl overflow-hidden">
        <div className="grid lg:grid-cols-[0.95fr_1.05fr]">
          <div className="bg-brand-600 p-8 text-white sm:p-10">
            <Logo />
            <div className="mt-12 max-w-md">
              <p className="text-xs font-semibold uppercase tracking-[0.28em] text-brand-100">
                Account setup
              </p>
              <h1 className="mt-4 text-4xl font-semibold leading-tight">
                Create the account that will anchor the protected app shell.
              </h1>
              <p className="mt-5 text-sm leading-7 text-brand-50/90">
                Registration uses the verified FastAPI auth module. Once you sign up, the
                frontend stores the JWT and refreshes the active user profile from
                `/auth/me`.
              </p>
            </div>
          </div>

          <div className="p-6 sm:p-8 lg:p-10">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-mint-700">
              Start here
            </p>
            <h2 className="mt-3 text-3xl font-semibold text-slate-900">Create your MediGen account</h2>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              This is the only real page flow in the frontend foundation because auth is
              required for protected routing.
            </p>

            <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
              <Input
                label="Full name"
                autoComplete="name"
                placeholder="Aarav Sharma"
                value={form.full_name}
                onChange={(event) =>
                  setForm((current) => ({ ...current, full_name: event.target.value }))
                }
              />
              <Input
                label="Email"
                type="email"
                autoComplete="email"
                placeholder="aarav@example.com"
                value={form.email}
                onChange={(event) =>
                  setForm((current) => ({ ...current, email: event.target.value }))
                }
              />
              <Input
                label="Password"
                type="password"
                autoComplete="new-password"
                placeholder="At least 8 characters with letters and digits"
                value={form.password}
                hint="The backend requires at least one letter and one digit."
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
                icon={<UserPlus className="h-4 w-4" />}
              >
                Create account
              </Button>
            </form>

            <p className="mt-6 text-sm text-slate-600">
              Already registered?{" "}
              <Link className="font-semibold text-brand-700 hover:text-brand-800" to="/login">
                Sign in instead
              </Link>
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
