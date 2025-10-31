
import React, { useState } from 'react';
import type { UserProfile } from '../types';

interface ProfileScreenProps {
  profiles: UserProfile[];
  onSelectProfile: (profile: UserProfile) => void;
  onCreateProfile: (name: string) => void;
}

const ProfileScreen: React.FC<ProfileScreenProps> = ({ profiles, onSelectProfile, onCreateProfile }) => {
  const [newProfileName, setNewProfileName] = useState('');

  const handleCreate = () => {
    if (newProfileName.trim()) {
      onCreateProfile(newProfileName.trim());
      setNewProfileName('');
    }
  };

  return (
    <div className="text-center max-w-md mx-auto">
      <h1 className="text-4xl font-bold text-sky-700 mb-4">학습자 선택</h1>
      <p className="text-lg text-gray-600 mb-8">계속하려면 프로필을 선택하거나 새로 만드세요.</p>

      {profiles.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">기존 프로필:</h2>
          <div className="flex flex-wrap justify-center gap-4">
            {profiles.map(profile => (
              <button
                key={profile.name}
                onClick={() => onSelectProfile(profile)}
                className="bg-sky-500 text-white font-bold py-3 px-6 rounded-lg text-lg hover:bg-sky-600 transition-colors"
              >
                {profile.name}
              </button>
            ))}
          </div>
        </div>
      )}

      <div>
        <h2 className="text-xl font-semibold text-gray-800 mb-4">새 프로필 만들기:</h2>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <input
            type="text"
            placeholder="학생 이름을 입력하세요"
            value={newProfileName}
            onChange={(e) => setNewProfileName(e.target.value)}
            className="text-lg p-2 border-2 border-gray-300 rounded-lg focus:border-sky-500 focus:ring-sky-500 flex-grow"
            onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
          />
          <button
            onClick={handleCreate}
            className="bg-green-500 text-white font-bold py-3 px-6 rounded-lg text-lg hover:bg-green-600 transition-colors"
          >
            만들기
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProfileScreen;