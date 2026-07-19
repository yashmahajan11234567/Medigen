import { ProfileHeader } from "@/pages/profile/components/ProfileHeader";
import { UserCard } from "@/pages/profile/components/UserCard";
import { HealthSummary } from "@/pages/profile/components/HealthSummary";
import { PersonalInfoCard } from "@/pages/profile/components/PersonalInfoCard";
import { SettingsSection } from "@/pages/profile/components/SettingsSection";
import { PreferenceToggle } from "@/pages/profile/components/PreferenceToggle";
import { ConnectedServices } from "@/pages/profile/components/ConnectedServices";
import { AboutCard } from "@/pages/profile/components/AboutCard";
import { LogoutButton } from "@/pages/profile/components/LogoutButton";

export function ProfilePage() {
  return (
    <div className="space-y-6">
      <ProfileHeader />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-5">
        <div className="space-y-6 lg:col-span-3">
          <UserCard />
          <HealthSummary />
          <PersonalInfoCard />
        </div>

        <div className="space-y-6 lg:col-span-2">
          <SettingsSection />
          <PreferenceToggle />
          <ConnectedServices />
          <AboutCard />
          <LogoutButton />
        </div>
      </div>
    </div>
  );
}