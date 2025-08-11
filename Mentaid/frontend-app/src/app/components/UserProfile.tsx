'use client';

import { FaUser, FaStethoscope, FaSignOutAlt } from 'react-icons/fa';

interface User {
  id: string;
  email: string;
  role: 'regular_user' | 'clinician';
  full_name?: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

interface UserProfileProps {
  user: User;
  onLogout: () => void;
  showFullProfile?: boolean;
}

export default function UserProfile({ user, onLogout, showFullProfile = true }: UserProfileProps) {
  const getUserInitials = (name: string | undefined, email: string) => {
    if (name) {
      return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    }
    return email.slice(0, 2).toUpperCase();
  };

  const getRoleIcon = () => {
    return user.role === 'clinician' ? FaStethoscope : FaUser;
  };

  const getRoleLabel = () => {
    return user.role === 'clinician' ? 'Clinician' : 'Patient';
  };

  const getAvatarClass = () => {
    return user.role === 'clinician' 
      ? 'user-avatar clinician'
      : 'user-avatar';
  };

  const getUserDisplayName = () => {
    if (user.role === 'clinician') {
      return `Dr. ${user.full_name || user.email.split('@')[0]}`;
    }
    return user.full_name || user.email.split('@')[0];
  };

  const RoleIcon = getRoleIcon();

  return (
    <div className="flex items-center space-x-4">
      {showFullProfile && (
        <div className="flex items-center space-x-3">
          <div className="relative">
            <div className={getAvatarClass()}>
              {getUserInitials(user.full_name, user.email)}
            </div>
            <div className="status-indicator"></div>
          </div>
          <div className="hidden sm:block">
            <p className="text-sm font-medium text-gray-900">{getUserDisplayName()}</p>
            <p className="text-xs text-gray-500 flex items-center">
              <RoleIcon className="mr-1" />
              {getRoleLabel()}
            </p>
          </div>
        </div>
      )}
      
      {showFullProfile && <div className="h-8 w-px bg-gray-300"></div>}
      
      <button
        onClick={onLogout}
        className="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-50 rounded-lg transition-all duration-200"
      >
        <FaSignOutAlt />
        <span className="hidden sm:inline">Logout</span>
      </button>
    </div>
  );
}