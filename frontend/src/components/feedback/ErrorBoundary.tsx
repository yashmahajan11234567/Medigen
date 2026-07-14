import { Component, type ErrorInfo, type ReactNode } from "react";
import { RotateCcw } from "lucide-react";
import { Button } from "@/components/common/Button";
import { Card } from "@/components/common/Card";
import { appConfig } from "@/lib/app-config";

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
}

export class AppErrorBoundary extends Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  state: ErrorBoundaryState = {
    hasError: false,
  };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("AppErrorBoundary", error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false });
    window.location.assign("/");
  };

  render() {
    if (!this.state.hasError) {
      return this.props.children;
    }

    return (
      <div className="flex min-h-screen items-center justify-center px-6">
        <Card className="w-full max-w-lg p-8">
          <span className="text-xs font-semibold uppercase tracking-[0.26em] text-brand-600">
            {appConfig.appName}
          </span>
          <h1 className="mt-3 text-3xl font-semibold text-slate-900">
            The app shell hit an unexpected problem
          </h1>
          <p className="mt-3 text-sm leading-7 text-slate-600">
            The frontend foundation is still safe to reload. No backend data was changed,
            and you can jump back in once the interface restarts.
          </p>
          <div className="mt-6">
            <Button onClick={this.handleReset} icon={<RotateCcw className="h-4 w-4" />}>
              Reload MediGen
            </Button>
          </div>
        </Card>
      </div>
    );
  }
}
