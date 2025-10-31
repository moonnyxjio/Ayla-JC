
import React from 'react';
import type { Story, ProgressData } from '../types';

interface BookScreenProps {
  story: Story;
  progress: ProgressData;
  onSelectDay: (dayIndex: number) => void;
  onGoHome: () => void;
}

const BookScreen: React.FC<BookScreenProps> = ({ story, progress, onSelectDay, onGoHome }) => {
  return (
    <div className="text-center">
      <button onClick={onGoHome} className="absolute top-6 left-6 text-sky-600 hover:text-sky-800">
        &larr; 책 선택으로 돌아가기
      </button>
      <h1 className="text-3xl font-bold text-sky-700 mb-4">{story.title}</h1>
      <p className="text-lg text-gray-600 mb-8">학습할 Day를 선택하세요.</p>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-2xl mx-auto">
        {story.content.map((_, index) => {
          const isCompleted = progress[`${story.id}-${index}`];
          return (
            <div
              key={index}
              className={`p-8 rounded-xl shadow-md cursor-pointer transform hover:scale-110 transition-all duration-300 flex flex-col justify-center items-center ${isCompleted ? 'bg-green-300 hover:bg-green-400' : 'bg-sky-200 hover:bg-sky-300'}`}
              onClick={() => onSelectDay(index)}
            >
              <span className="text-4xl font-bold text-white">Day {index + 1}</span>
              {isCompleted && <span className="text-2xl mt-1">✔️</span>}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default BookScreen;