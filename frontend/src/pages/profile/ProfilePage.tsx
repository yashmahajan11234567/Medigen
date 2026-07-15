import { useNavigate } from "react-router-dom";
import { PageIntro } from "@/components/common/PageIntro";
import { Button } from "@/components/common/Button";
import { Card } from "@/components/common/Card";
import { LoadingScreen } from "@/components/common/LoadingScreen";
import { InlineError } from "@/components/feedback/InlineError";
import { useProfile } from "@/hooks/useProfile";
import { LogOut, RefreshCw } from "lucide-react";

export function ProfilePage() {
  const { user, loading, error, refetch } = useProfile();
  const navigate = useNavigate();

  const handleRefresh = () => {
    void refetch();
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login", { replace: true });
  };

  if (error) {
    return (
      <>
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
          <InlineError title="Error" message={error} />
        </div>
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <Button
              variant="secondary"
              size="sm"
              onClick={handleRefresh}
            >
              <RefreshCw className="mr-2" /> Refresh
            </Button>
          </div>
          <Card>
            <div className="p-6">
              <p className="text-red-600">Failed to load profile. Please try again.</p>
              <Button
                variant="secondary"
                size="sm"
                onClick={handleRefresh}
                className="mt-4"
              >
                Retry
              </Button>
            </div>
          </Card>
        </div>
      </>
    );
  }

  if (loading || !user) {
    return (
      <>
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <Button
              variant="secondary"
              size="sm"
              onClick={handleRefresh}
            >
              <RefreshCw className="mr-2" /> Refresh
            </Button>
          </div>
          <Card>
            <LoadingScreen
              title="Loading profile…"
              description="Please wait while we load your profile information."
            />
          </Card>
        </div>
      </>
    );
  }

  return (
    <>
      <PageIntro
        eyebrow="Profile"
        title="My Profile"
        description="View and manage your profile information"
      />
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <Button
            variant="secondary"
            size="sm"
            onClick={handleRefresh}
          >
            <RefreshCw className="mr-2" /> Refresh
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={handleLogout}
          >
            <LogOut className="mr-2" /> Log Out
          </Button>
        </div>
        <Card>
          <div className="space-y-4">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Full Name</p>
              <p className="text-lg font-semibold">{user.full_name}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Email</p>
              <p className="text-lg font-semibold break-all">{user.email}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Username</p>
              <p className="text-lg font-semibold">{user.email.split("@")[0]}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Account Status</p>
              <p className={`text-lg font-semibold ${user.is_active ? "text-green-600" : "text-red-600"}`}>
                {user.is_active ? "Active" : "Inactive"}
              </p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Role</p>
              <p className="text-lg font-semibold">
                {user.is_superuser ? "Administrator" : "User"}
              </p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Created At</p>
              <p className="text-lg font-semibold">
                {new Date(user.created_at).toLocaleDateString()}
              </p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Updated At</p>
              <p className="text-lg font-semibold">
                {new Date(user.updated_at).toLocaleDateString()}
              </p>
            </div>
          </div>
        </Card>
      </div>
    </>
  );
}