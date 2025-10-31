import React, { useState, useCallback, useEffect } from 'react';
import type { Story, Question, IncorrectAnswer, QuizResult, WordAnalyses, SpellingQuestion, ScrambleQuestion, SentenceAnalysisData, ReadingQuestion, UserProfile } from '../types';
import { analyzeSentencesForDay } from '../services/geminiService';

interface QuizScreenProps {
  story: Story;
  dayIndex: number;
  currentUser: UserProfile;
  onFinishQuiz: (result: QuizResult) => void;
  onGoHome: () => void;
}

const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

// --- Question Generation ---
const generateSpellingQuestions = (wordAnalyses: WordAnalyses): { type: 'spelling', data: SpellingQuestion }[] => {
    const words = Object.keys(wordAnalyses);
    return words.sort(() => 0.5 - Math.random()).slice(0, 6).map(word => ({
        type: 'spelling' as const,
        data: { word, phonics: wordAnalyses[word].phonics, koreanMeaning: wordAnalyses[word].koreanMeaning }
    }));
};

const generateScrambleQuestions = (sentenceData: { sentence: string, analysis: SentenceAnalysisData | null }[]): { type: 'scramble', data: ScrambleQuestion }[] => {
    return sentenceData.sort(() => 0.5 - Math.random()).slice(0, 2).map(({ sentence, analysis }) => {
        const cleanSentence = sentence.replace(/[.,?!"]/g, '');
        return {
            type: 'scramble' as const,
            data: { 
                sentence: cleanSentence.split(' ').sort(() => 0.5 - Math.random()),
                originalSentence: cleanSentence,
                translationHint: analysis?.chunkedTranslation.replace(/ \/ /g, ' ') || "힌트 없음"
            }
        };
    });
};

const generateReadAllSentencesQuiz = (sentences: string[]): { type: 'reading', data: ReadingQuestion }[] => {
    return sentences.map(sentence => ({
        type: 'reading' as const,
        data: { sentence }
    }));
};


const QuizScreen: React.FC<QuizScreenProps> = ({ story, dayIndex, currentUser, onFinishQuiz, onGoHome }) => {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState<(string | string[])[]>([]);
  
  // State for different answer types
  const [currentSpellingAnswer, setCurrentSpellingAnswer] = useState('');
  const [currentScrambleAnswer, setCurrentScrambleAnswer] = useState<string[]>([]);
  const [scrambleWordBank, setScrambleWordBank] = useState<string[]>([]);
  
  // State for speech recognition
  const [isListening, setIsListening] = useState(false);
  const [speechResult, setSpeechResult] = useState<string | null>(null);
  let recognition: any;

  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
  }

  // --- Setup ---
  useEffect(() => {
    const setupQuiz = async () => {
        setIsLoading(true);
        const allSentences = story.content[dayIndex];
        
        const allAnalysesRecord = await analyzeSentencesForDay(allSentences, story.id, dayIndex);
        
        const combinedWordAnalyses: WordAnalyses = Object.values(allAnalysesRecord).reduce((acc, current) => {
            return current ? { ...acc, ...current.wordAnalyses } : acc;
        }, {});
        
        const sentenceData = allSentences.map(sentence => ({
            sentence,
            analysis: allAnalysesRecord[sentence] || null
        }));

        const spellingQs = generateSpellingQuestions(combinedWordAnalyses);
        const scrambleQs = generateScrambleQuestions(sentenceData);
        const readingQs = generateReadAllSentencesQuiz(allSentences);
        
        // A fixed order might be better for user experience
        const allQuestions = [...spellingQs, ...scrambleQs, ...readingQs];
        setQuestions(allQuestions);
        setIsLoading(false);
    };
    setupQuiz();
  }, [story, dayIndex]);

  const currentQuestion = questions[currentQuestionIndex];

  useEffect(() => {
    if (currentQuestion?.type === 'scramble') {
        setScrambleWordBank(currentQuestion.data.sentence);
        setCurrentScrambleAnswer([]);
    }
  }, [currentQuestion]);

  // --- Handlers ---
  const handleNextQuestion = () => {
    let answerToSave: string | string[];
    switch(currentQuestion.type) {
        case 'spelling': answerToSave = currentSpellingAnswer; break;
        case 'scramble': answerToSave = currentScrambleAnswer; break;
        case 'reading': answerToSave = speechResult || ''; break;
        default: answerToSave = '';
    }

    const newAnswers = [...userAnswers, answerToSave];
    setUserAnswers(newAnswers);

    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setCurrentSpellingAnswer('');
      setSpeechResult(null);
    } else {
      finishQuiz(newAnswers);
    }
  };

  const handleSpeechRecognition = () => {
    if (!recognition) return alert("음성 인식이 지원되지 않는 브라우저입니다.");
    if (isListening) return recognition.stop();
    
    setSpeechResult(null);
    setIsListening(true);
    
    recognition.onresult = (event: any) => setSpeechResult(event.results[0][0].transcript);
    recognition.onerror = (event: any) => console.error("Speech recognition error", event.error);
    recognition.onend = () => setIsListening(false);
    
    recognition.start();
  };

  const finishQuiz = useCallback((finalAnswers: (string | string[])[]) => {
    const incorrectAnswers: IncorrectAnswer[] = [];
    let score = 0;
    let spellingCorrect = 0, scrambleCorrect = 0, readingCorrect = 0;
    
    const spellingTotal = questions.filter(q => q.type === 'spelling').length;
    const scrambleTotal = questions.filter(q => q.type === 'scramble').length;
    const readingTotal = questions.filter(q => q.type === 'reading').length;

    questions.forEach((q, i) => {
        const userAnswer = finalAnswers[i];
        
        if (q.type === 'spelling') {
            const correctAnswer = q.data.word;
            if ((userAnswer as string).toLowerCase().trim() === correctAnswer.toLowerCase()) {
                score++; spellingCorrect++;
            } else {
                incorrectAnswers.push({ type: 'spelling', question: `뜻: ${q.data.koreanMeaning}`, userAnswer: userAnswer as string, correctAnswer });
            }
        } else if (q.type === 'scramble') {
            const correctAnswer = q.data.originalSentence;
            const userAnswerString = (userAnswer as string[]).join(' ');
            if (userAnswerString.toLowerCase().trim() === correctAnswer.toLowerCase().trim()) {
                score++; scrambleCorrect++;
            } else {
                incorrectAnswers.push({ type: 'scramble', question: q.data.sentence.join(' '), userAnswer: userAnswerString, correctAnswer });
            }
        } else if (q.type === 'reading') {
            const correctAnswer = q.data.sentence.replace(/[.,?!"]/g, '').toLowerCase().trim();
            const userAnswerString = (userAnswer as string).replace(/[.,?!"]/g, '').toLowerCase().trim();
            if (userAnswerString === correctAnswer) {
                score++; readingCorrect++;
            } else {
                incorrectAnswers.push({ type: 'reading', question: q.data.sentence, userAnswer: userAnswer as string, correctAnswer: q.data.sentence });
            }
        }
    });
    
    onFinishQuiz({
      storyId: story.id,
      storyTitle: story.title, 
      day: dayIndex + 1, 
      score, 
      totalQuestions: questions.length,
      spellingScore: { correct: spellingCorrect, total: spellingTotal },
      scrambleScore: { correct: scrambleCorrect, total: scrambleTotal },
      readingScore: { correct: readingCorrect, total: readingTotal },
      incorrectAnswers,
      studentName: currentUser.name
    });
  }, [questions, story, dayIndex, onFinishQuiz, currentUser.name]);

  const handleWordBankClick = (word: string, index: number) => {
    setCurrentScrambleAnswer([...currentScrambleAnswer, word]);
    setScrambleWordBank(prev => prev.filter((_, i) => i !== index));
  };

  const handleAnswerAreaClick = (word: string, index: number) => {
    setCurrentScrambleAnswer(prev => prev.filter((_, i) => i !== index));
    setScrambleWordBank(prev => [...prev, word].sort(() => 0.5 - Math.random()));
  };
  
  // --- Render ---
  if (isLoading) return <div className="text-center p-10">퀴즈를 준비하고 있어요...</div>;
  if (!currentQuestion) return <div className="text-center p-10">퀴즈를 불러오는데 실패했어요.</div>;

  return (
    <div className="text-center">
      <button onClick={onGoHome} className="absolute top-6 left-6 text-sky-600 hover:text-sky-800">&larr; 홈으로</button>
      <h1 className="text-3xl font-bold text-sky-700 mb-4">Day {dayIndex + 1} 퀴즈</h1>
      <p className="text-lg text-gray-600 mb-8">문제 {currentQuestionIndex + 1} / {questions.length}</p>

      <div className="bg-gray-50 p-6 rounded-lg shadow-inner min-h-[300px] flex flex-col justify-center">
        {currentQuestion.type === 'spelling' && (
          <div>
            <h2 className="text-xl font-semibold text-gray-800 mb-4">다음 단어의 스펠링을 입력하세요:</h2>
            <div className="mb-6">
                <p className="text-2xl font-bold text-gray-700">뜻: <span className="text-blue-600">{currentQuestion.data.koreanMeaning}</span></p>
                <p className="text-2xl font-bold text-gray-700">파닉스: <span className="text-blue-600 tracking-widest">{currentQuestion.data.phonics}</span></p>
            </div>
            <input type="text" value={currentSpellingAnswer} onChange={(e) => setCurrentSpellingAnswer(e.target.value)}
              className="text-center text-2xl p-2 border-2 border-gray-300 rounded-lg w-full max-w-sm focus:border-blue-500 focus:ring-blue-500"
              autoCapitalize="none" autoComplete="off" />
          </div>
        )}
        {currentQuestion.type === 'scramble' && (
          <div>
            <h2 className="text-xl font-semibold text-gray-800 mb-2">문장을 순서대로 배열하세요:</h2>
            <p className="text-gray-600 mb-4">힌트: "{currentQuestion.data.translationHint}"</p>
            <div className="bg-white p-4 rounded-lg min-h-[60px] border border-gray-300 mb-4 flex flex-wrap gap-2 justify-center items-center">
                {currentScrambleAnswer.map((word, i) => (
                    <button key={i} onClick={() => handleAnswerAreaClick(word, i)} className="bg-blue-500 text-white font-semibold py-2 px-4 rounded-lg">{word}</button>
                ))}
            </div>
            <div className="flex flex-wrap gap-2 justify-center items-center">
              {scrambleWordBank.map((word, i) => (
                <button key={i} onClick={() => handleWordBankClick(word, i)} className="bg-gray-200 text-gray-800 font-semibold py-2 px-4 rounded-lg hover:bg-gray-300">{word}</button>
              ))}
            </div>
          </div>
        )}
        {currentQuestion.type === 'reading' && (
            <div>
                <h2 className="text-xl font-semibold text-gray-800 mb-4">다음 문장을 소리내어 읽어보세요:</h2>
                <p className="text-2xl font-bold text-gray-700 mb-6 p-4 bg-white rounded-lg">{currentQuestion.data.sentence}</p>
                 <div className="mt-4">
                    <button onClick={handleSpeechRecognition} disabled={!SpeechRecognition} className={`font-bold py-2 px-4 rounded-lg transition-colors ${isListening ? 'bg-red-500 hover:bg-red-600' : 'bg-green-500 hover:bg-green-600'} text-white disabled:bg-gray-300 w-full max-w-sm mx-auto`}>
                        {isListening ? '녹음 중...' : '마이크 버튼을 눌러 말하기 🎤'}
                    </button>
                    {speechResult && (
                        <div className="mt-4 p-2 bg-gray-200 rounded-lg">
                            <p className="text-gray-800">내 답변: "{speechResult}"</p>
                        </div>
                    )}
                </div>
            </div>
        )}
      </div>

      <div className="mt-8">
        <button onClick={handleNextQuestion} className="bg-green-500 text-white font-bold py-3 px-8 rounded-lg text-lg hover:bg-green-600 transition-colors">
          {currentQuestionIndex < questions.length - 1 ? '다음 문제' : '결과 보기'}
        </button>
      </div>
    </div>
  );
};

export default QuizScreen;