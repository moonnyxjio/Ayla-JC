
import React, { useState, useEffect } from 'react';
import HomeScreen from './components/HomeScreen';
import BookScreen from './components/BookScreen';
import LearningScreen from './components/LearningScreen';
import QuizScreen from './components/QuizScreen';
import CertificationScreen from './components/CertificationScreen';
import AdminScreen from './components/AdminScreen';
import ProfileScreen from './components/ProfileScreen';
import { stories } from './data/stories';
import type { Story, QuizResult, View, UserProfile, ProgressData } from './types';

const App: React.FC = () => {
  const [view, setView] = useState<View>('profiles');
  const [selectedStory, setSelectedStory] = useState<Story | null>(null);
  const [selectedDay, setSelectedDay] = useState<number | null>(null);
  const [quizResult, setQuizResult] = useState<QuizResult | null>(null);
  
  // User Profile State
  const [profiles, setProfiles] = useState<UserProfile[]>([]);
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(null);
  const [progressData, setProgressData] = useState<ProgressData>({});

  // Load profiles from localStorage on initial render
  useEffect(() => {
    try {
      const storedProfiles = JSON.parse(localStorage.getItem('profiles') || '[]');
      setProfiles(storedProfiles);
      const lastUserName = localStorage.getItem('lastUserProfileName');
      if (lastUserName) {
        const lastUser = storedProfiles.find((p: UserProfile) => p.name === lastUserName);
        if (lastUser) {
          handleSelectProfile(lastUser);
        }
      }
    } catch (e) {
      console.error("Failed to load profiles from local storage", e);
      setProfiles([]);
    }
  }, []);

  const handleSelectProfile = (profile: UserProfile) => {
    setCurrentUser(profile);
    try {
      const storedProgress = JSON.parse(localStorage.getItem(`progress-${profile.name}`) || '{}');
      setProgressData(storedProgress);
      localStorage.setItem('lastUserProfileName', profile.name);
    } catch (e) {
      console.error("Failed to load user progress", e);
      setProgressData({});
    }
    setView('home');
  };

  const handleCreateProfile = (name: string) => {
    if (name.trim() && !profiles.some(p => p.name === name.trim())) {
      const newProfile: UserProfile = { name: name.trim() };
      const updatedProfiles = [...profiles, newProfile];
      setProfiles(updatedProfiles);
      try {
        localStorage.setItem('profiles', JSON.stringify(updatedProfiles));
      } catch (e) {
        console.error("Failed to save profiles", e);
      }
      handleSelectProfile(newProfile);
    } else {
      alert("Invalid or duplicate name.");
    }
  };

  const handleSwitchProfile = () => {
    setCurrentUser(null);
    setProgressData({});
    try {
      localStorage.removeItem('lastUserProfileName');
    } catch(e) {
       console.error("Failed to clear last user", e);
    }
    setView('profiles');
  };

  const handleSelectStory = (storyId: string) => {
    const story = stories.find(s => s.id === storyId);
    if (story) {
      setSelectedStory(story);
      setView('book');
    }
  };

  const handleSelectDay = (dayIndex: number) => {
    setSelectedDay(dayIndex);
    setView('learning');
  };

  const handleFinishLearning = () => {
    setView('quiz');
  };

  const handleFinishQuiz = (result: QuizResult) => {
    setQuizResult(result);
    setView('certification');
  };

  const handleSaveProgress = (result: QuizResult) => {
    if (!currentUser) return;
    
    // Update this user's progress data
    const progressKey = `${result.storyId}-${result.day - 1}`;
    const updatedProgress = { ...progressData, [progressKey]: true };
    setProgressData(updatedProgress);

    try {
      // Save this user's progress
      localStorage.setItem(`progress-${currentUser.name}`, JSON.stringify(updatedProgress));
      
      // Save the quiz result to the global list for the admin screen
      const existingResults: QuizResult[] = JSON.parse(localStorage.getItem('studentResults') || '[]');
      existingResults.push(result);
      localStorage.setItem('studentResults', JSON.stringify(existingResults));
    } catch (e) {
      console.error("Failed to save progress or results", e);
    }
  };
  
  const handleGoHome = () => {
    setView('home');
    setSelectedStory(null);
    setSelectedDay(null);
    setQuizResult(null);
  };
  
  const handleViewAdmin = () => {
    setView('admin');
  };

  const renderView = () => {
    switch (view) {
      case 'profiles':
        return <ProfileScreen profiles={profiles} onSelectProfile={handleSelectProfile} onCreateProfile={handleCreateProfile} />;
      case 'home':
        return <HomeScreen 
          currentUser={currentUser!} 
          progress={progressData}
          onSelectStory={handleSelectStory} 
          onAdminClick={handleViewAdmin} 
          onSwitchProfile={handleSwitchProfile}
        />;
      case 'book':
        return <BookScreen 
          story={selectedStory!} 
          progress={progressData}
          onSelectDay={handleSelectDay} 
          onGoHome={handleGoHome} 
        />;
      case 'learning':
        return <LearningScreen story={selectedStory!} dayIndex={selectedDay!} onFinish={handleFinishLearning} onGoHome={handleGoHome} />;
      case 'quiz':
        return <QuizScreen story={selectedStory!} dayIndex={selectedDay!} currentUser={currentUser!} onFinishQuiz={handleFinishQuiz} onGoHome={handleGoHome} />;
      case 'certification':
        return <CertificationScreen result={quizResult!} onSaveProgress={handleSaveProgress} onGoHome={handleGoHome} />;
      case 'admin':
        return <AdminScreen onGoHome={handleGoHome} />;
      default:
        return <ProfileScreen profiles={profiles} onSelectProfile={handleSelectProfile} onCreateProfile={handleCreateProfile} />;
    }
  };

  return (
    <div className="min-h-screen bg-sky-100 font-sans p-4 sm:p-6 md:p-8">
      <div className="max-w-4xl mx-auto bg-white rounded-2xl shadow-lg p-6 relative">
        {renderView()}
      </div>
    </div>
  );
};

export default App;