
import React from 'react';
import { stories } from '../data/stories';
import type { Story, UserProfile, ProgressData } from '../types';

interface HomeScreenProps {
  currentUser: UserProfile;
  progress: ProgressData;
  onSelectStory: (storyId: string) => void;
  onAdminClick: () => void;
  onSwitchProfile: () => void;
}

const ProgressBar: React.FC<{story: Story, progress: ProgressData}> = ({ story, progress }) => {
  const totalDays = story.content.length;
  let completedDays = 0;
  for (let i = 0; i < totalDays; i++) {
    if (progress[`${story.id}-${i}`]) {
      completedDays++;
    }
  }
  const progressPercentage = totalDays > 0 ? (completedDays / totalDays) * 100 : 0;

  return (
    <div className="w-full bg-gray-200 rounded-full h-2.5 mt-2">
      <div className="bg-green-500 h-2.5 rounded-full" style={{ width: `${progressPercentage}%` }}></div>
    </div>
  );
};

const HomeScreen: React.FC<HomeScreenProps> = ({ currentUser, progress, onSelectStory, onAdminClick, onSwitchProfile }) => {
  return (
    <div className="text-center">
      <div className="flex justify-between items-center mb-2">
          <button onClick={onSwitchProfile} className="text-sm text-sky-600 hover:underline">
            Switch Profile
          </button>
          <div />
      </div>
      <h1 className="text-4xl font-bold text-sky-700 mb-2">Welcome, {currentUser.name}!</h1>
      <p className="text-lg text-gray-600 mb-8">학습할 동화책을 선택하세요.</p>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {stories.map((story: Story) => (
          <div
            key={story.id}
            className="cursor-pointer group transform hover:scale-105 transition-transform duration-300"
            onClick={() => onSelectStory(story.id)}
          >
            <div className="relative">
              <img src={story.coverImage} alt={story.title} className="rounded-lg shadow-lg w-full h-auto object-cover aspect-[4/5]" />
            </div>
            <h2 className="mt-4 text-md font-semibold text-gray-800 group-hover:text-sky-600">{story.title}</h2>
            <ProgressBar story={story} progress={progress} />
          </div>
        ))}
      </div>
      <div className="mt-12 text-right">
        <button 
          onClick={onAdminClick}
          className="bg-gray-200 text-gray-700 font-semibold py-2 px-4 rounded-lg hover:bg-gray-300 transition-colors"
        >
          선생님 화면 (관리자 모드)
        </button>
      </div>
    </div>
  );
};

export default HomeScreen;