
import React, { useState, useRef, useEffect } from 'react';
import type { QuizResult } from '../types';
import { generatePersonalizedFeedback } from '../services/geminiService';

// Let TypeScript know that html2canvas is available on the window object
declare const html2canvas: any;

interface CertificationScreenProps {
  result: QuizResult;
  onSaveProgress: (result: QuizResult) => void;
  onGoHome: () => void;
}

const CertificationScreen: React.FC<CertificationScreenProps> = ({ result, onSaveProgress, onGoHome }) => {
  const [isSaved, setIsSaved] = useState(false);
  const certificateRef = useRef<HTMLDivElement>(null);
  const studentName = result.studentName;

  const [feedback, setFeedback] = useState<string>('');
  const [isFeedbackLoading, setIsFeedbackLoading] = useState(true);

  useEffect(() => {
    const getFeedback = async () => {
      setIsFeedbackLoading(true);
      const message = await generatePersonalizedFeedback(result);
      setFeedback(message);
      setIsFeedbackLoading(false);
    };
    
    getFeedback();
  }, [result]);

  const handleSave = () => {
    onSaveProgress(result);
    setIsSaved(true);
  };

  const handleDownloadImage = () => {
    if (!certificateRef.current) {
      return;
    }
    html2canvas(certificateRef.current).then((canvas: HTMLCanvasElement) => {
      const link = document.createElement('a');
      link.download = `certificate-${studentName.trim()}-Day${result.day}.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
    });
  };

  const getQuizTypeName = (type: string) => {
    switch (type) {
        case 'spelling': return '스펠링';
        case 'scramble': return '문장 배열';
        case 'reading': return '따라 읽기';
        default: return '퀴즈';
    }
  }

  return (
    <div className="text-center">
      <h1 className="text-3xl font-bold text-yellow-500 mb-6">참 잘했어요!</h1>
      
      <div ref={certificateRef} className="bg-white p-8 rounded-lg shadow-xl border-4 border-yellow-400 max-w-2xl mx-auto">
        <h2 className="text-2xl font-bold text-sky-700">학습 인증서</h2>
        <p className="text-lg text-gray-600 mt-2 mb-6">Certificate of Achievement</p>
        
        <div className="text-left space-y-4 text-gray-800">
          <p><strong className="w-32 inline-block">학생 이름:</strong> <span className="font-semibold text-black">{studentName}</span></p>
          <p><strong className="w-32 inline-block">학습한 책:</strong> {result.storyTitle}</p>
          <p><strong className="w-32 inline-block">학습한 Day:</strong> Day {result.day}</p>
          <hr className="my-4"/>
          <p className="text-xl font-bold text-green-600"><strong className="w-32 inline-block text-gray-800">총 점수:</strong> {result.totalQuestions > 0 ? Math.round((result.score / result.totalQuestions) * 100) : 0}점</p>
          <div>
            <p><strong className="w-32 inline-block">상세 점수:</strong></p>
            <ul className="list-disc list-inside ml-4 text-gray-700">
              {result.spellingScore.total > 0 && <li>스펠링 퀴즈: {result.spellingScore.correct} / {result.spellingScore.total}</li>}
              {result.scrambleScore.total > 0 && <li>문장 배열 퀴즈: {result.scrambleScore.correct} / {result.scrambleScore.total}</li>}
              {result.readingScore.total > 0 && <li>따라 읽기 퀴즈: {result.readingScore.correct} / {result.readingScore.total}</li>}
            </ul>
          </div>

          <div>
            <p><strong className="w-32 inline-block">AI 선생님의 한마디:</strong></p>
            <div className="mt-2 p-4 bg-sky-50 rounded-lg border border-sky-200">
              {isFeedbackLoading ? (
                <p className="text-gray-500 italic">선생님께서 코멘트를 작성하고 있어요...</p>
              ) : (
                <p className="text-sky-800 font-medium whitespace-pre-wrap">{feedback}</p>
              )}
            </div>
          </div>
          
          {result.incorrectAnswers.length > 0 && (
            <div>
              <p><strong className="w-32 inline-block">틀린 문제:</strong></p>
              <ul className="list-disc list-inside ml-4 text-red-600">
                {result.incorrectAnswers.map((ans, i) => (
                  <li key={i}>({getQuizTypeName(ans.type)}) {ans.correctAnswer}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {!isSaved ? (
        <div className="mt-6 flex flex-col sm:flex-row gap-4 justify-center items-center">
          <button 
            onClick={handleSave}
            className="bg-sky-500 text-white font-bold py-3 px-8 rounded-lg text-lg hover:bg-sky-600 transition-colors"
          >
            결과 저장하기
          </button>
        </div>
      ) : (
        <div className="mt-6 flex flex-col items-center gap-4">
            <p className="text-xl font-semibold text-green-600">저장되었습니다!</p>
            <button
                onClick={handleDownloadImage}
                className="bg-yellow-500 text-white font-bold py-3 px-8 rounded-lg text-lg hover:bg-yellow-600 transition-colors"
            >
                인증서 이미지로 다운로드
            </button>
        </div>
      )}

      <button onClick={onGoHome} className="mt-8 bg-gray-500 text-white font-bold py-3 px-8 rounded-lg text-lg hover:bg-gray-600 transition-colors">
        홈으로 돌아가기
      </button>
    </div>
  );
};

export default CertificationScreen;
