import React, { useState, useEffect, useMemo } from 'react';
import type { QuizResult } from '../types';

interface AdminScreenProps {
  onGoHome: () => void;
}

const AdminScreen: React.FC<AdminScreenProps> = ({ onGoHome }) => {
  const [results, setResults] = useState<QuizResult[]>([]);

  useEffect(() => {
    const storedResults = JSON.parse(localStorage.getItem('studentResults') || '[]').reverse();
    setResults(storedResults);
  }, []);

  const getQuizTypeName = (type: string) => {
    switch (type) {
        case 'spelling': return '스펠링 퀴즈';
        case 'scramble': return '문장 배열 퀴즈';
        case 'reading': return '따라 읽기 퀴즈';
        default: return '퀴즈';
    }
  }

  const groupedResults = useMemo(() => {
    return results.reduce((acc, result) => {
      const studentName = result.studentName || 'Unknown Student';
      if (!acc[studentName]) {
        acc[studentName] = [];
      }
      acc[studentName].push(result);
      return acc;
    }, {} as Record<string, QuizResult[]>);
  }, [results]);

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-sky-700">학생별 학습 결과</h1>
        <button onClick={onGoHome} className="bg-gray-200 text-gray-700 font-semibold py-2 px-4 rounded-lg hover:bg-gray-300 transition-colors">
          홈으로 돌아가기
        </button>
      </div>

      {Object.keys(groupedResults).length === 0 ? (
        <p className="text-center text-gray-600 mt-12">아직 저장된 학습 결과가 없습니다.</p>
      ) : (
        <div className="space-y-8">
          {Object.entries(groupedResults).map(([studentName, studentResults]) => (
            <div key={studentName}>
                <h2 className="text-2xl font-bold text-gray-800 mb-4 pb-2 border-b-2 border-sky-300">{studentName}</h2>
                <div className="space-y-4">
                {studentResults.map((result, index) => (
                    <div key={index} className="bg-white p-4 rounded-lg shadow-md border border-gray-200">
                    <div className="flex flex-col sm:flex-row justify-between sm:items-center border-b pb-3 mb-3">
                        <div>
                        <h3 className="text-lg font-bold text-sky-800">{result.storyTitle} - Day {result.day}</h3>
                        </div>
                        <div className="text-right mt-2 sm:mt-0">
                            <p className="text-lg font-bold text-green-600">
                            총점: {result.totalQuestions > 0 ? Math.round((result.score / result.totalQuestions) * 100) : 0}점
                            </p>
                            <p className="text-xs text-gray-600">
                                (스펠링: {result.spellingScore.correct}/{result.spellingScore.total} | 
                                배열: {result.scrambleScore.correct}/{result.scrambleScore.total} | 
                                읽기: {result.readingScore.correct}/{result.readingScore.total})
                            </p>
                        </div>
                    </div>
                    
                    {result.incorrectAnswers.length > 0 ? (
                        <div>
                        <h4 className="text-md font-semibold text-red-700 mb-2">오답 노트</h4>
                        <ul className="space-y-2">
                            {result.incorrectAnswers.map((ans, i) => (
                            <li key={i} className="bg-red-50 p-3 rounded-md text-sm">
                                <p className="font-semibold text-red-900">
                                  {getQuizTypeName(ans.type)}
                                </p>
                                <p className="text-gray-700">문제: "{ans.question}"</p>
                                <p className="text-gray-700">정답: "{ans.correctAnswer}"</p>
                                <p className="text-red-800">학생 답: "{ans.userAnswer}"</p>
                            </li>
                            ))}
                        </ul>
                        </div>
                    ) : (
                        <p className="text-green-700 font-semibold">모든 문제를 맞췄습니다!</p>
                    )}
                    </div>
                ))}
                </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AdminScreen;