import React, { useState, useEffect, useMemo } from 'react';
import type { Story, SentenceAnalysisData } from '../types';
import { analyzeSentencesForDay, getSpeech } from '../services/geminiService';
import { playAudio } from '../services/audioService';

interface LearningScreenProps {
  story: Story;
  dayIndex: number;
  onFinish: () => void;
  onGoHome: () => void;
}

const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

const SentenceView: React.FC<{
  sentence: string;
  analysis: SentenceAnalysisData | null;
}> = ({ sentence, analysis }) => {
    const [isLoadingSound, setIsLoadingSound] = useState(false);
    const [isListening, setIsListening] = useState(false);
    const [speechResult, setSpeechResult] = useState<{transcript: string; isCorrect: boolean} | null>(null);
    let recognition: any;

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;
    }

    const handlePlaySound = async (text: string) => {
        // Prevent concurrent sound requests to improve UX
        if (isLoadingSound) return;

        setIsLoadingSound(true);
        const audioData = await getSpeech(text);
        if(audioData) {
            await playAudio(audioData);
        }
        setIsLoadingSound(false);
    }

    const handleSpeakingPractice = () => {
        if (!recognition) {
            alert("음성 인식이 지원되지 않는 브라우저입니다.");
            return;
        }
        if (isListening) {
            recognition.stop();
            setIsListening(false);
            return;
        }
        
        setSpeechResult(null);
        setIsListening(true);
        
        recognition.onresult = (event: any) => {
            const transcript = event.results[0][0].transcript;
            const cleanedOriginal = sentence.replace(/[.,?!"]/g, '').toLowerCase().trim();
            const cleanedTranscript = transcript.replace(/[.,?!"]/g, '').toLowerCase().trim();
            
            setSpeechResult({ transcript, isCorrect: cleanedOriginal === cleanedTranscript });
            setIsListening(false);
        };
        
        recognition.onerror = (event: any) => {
            console.error("Speech recognition error", event.error);
            setIsListening(false);
        };
        
        recognition.onend = () => {
            setIsListening(false);
        };
        
        recognition.start();
    };

    return (
        <div className="bg-gray-50 p-6 rounded-lg shadow-inner mb-6">
            <>
              <div className="flex justify-between items-start mb-4">
                  <p className="text-2xl leading-relaxed text-gray-800 flex flex-wrap items-baseline gap-x-2 gap-y-4">
                      {sentence.split(' ').map((word, i) => {
                          const cleanWord = word.replace(/[.,?!"]/g, '').toLowerCase();
                          const wordAnalysis = analysis?.wordAnalyses[cleanWord];
                          return (
                              <span key={i} className="inline-block text-center">
                                  <span
                                      onClick={() => wordAnalysis && handlePlaySound(cleanWord)}
                                      className={`
                                        ${wordAnalysis ? 'font-bold text-sky-700 hover:bg-yellow-200 cursor-pointer' : ''}
                                        ${isLoadingSound ? 'opacity-50 cursor-not-allowed' : ''}
                                        p-1 rounded transition-colors
                                      `}
                                  >
                                      {word}
                                  </span>
                                  {wordAnalysis && (
                                      <span className="block text-sm text-gray-600 font-medium pt-1">{wordAnalysis.koreanMeaning}</span>
                                  )}
                              </span>
                          );
                      })}
                  </p>
                  <button onClick={() => handlePlaySound(sentence)} disabled={isLoadingSound} className="bg-sky-500 text-white font-bold py-1 px-3 rounded-lg hover:bg-sky-600 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed text-sm ml-4 flex-shrink-0">
                      🔊
                  </button>
              </div>
              
              <div className="mt-4 p-3 bg-green-50 rounded-lg border border-green-200">
                  <h3 className="text-md font-bold text-green-800 mb-2">말하기 연습</h3>
                  <button onClick={handleSpeakingPractice} disabled={!SpeechRecognition} className={`w-full font-bold py-2 px-4 rounded-lg transition-colors ${isListening ? 'bg-red-500 hover:bg-red-600' : 'bg-green-500 hover:bg-green-600'} text-white disabled:bg-gray-300`}>
                      {isListening ? '듣고 있어요...' : '따라 말하기 🎤'}
                  </button>
                  {speechResult && (
                      <div className={`mt-3 p-2 rounded-lg text-center text-sm ${speechResult.isCorrect ? 'bg-blue-100 text-blue-800' : 'bg-red-100 text-red-800'}`}>
                          <p>{speechResult.isCorrect ? '정확해요! 👍' : '조금 달라요. 👎'}</p>
                          <p className="mt-1">내가 말한 문장: "{speechResult.transcript}"</p>
                      </div>
                  )}
              </div>
            </>
        </div>
    );
}

const LearningScreen: React.FC<LearningScreenProps> = ({ story, dayIndex, onFinish, onGoHome }) => {
  const [analyses, setAnalyses] = useState<Record<string, SentenceAnalysisData | null>>({});
  const [isLoading, setIsLoading] = useState(true);

  const sentences = useMemo(() => story.content[dayIndex], [story.content, dayIndex]);
  
  useEffect(() => {
    const analyzeAllSentences = async () => {
      setIsLoading(true);
      setAnalyses({}); // Clear previous analyses
      try {
        const results = await analyzeSentencesForDay(sentences, story.id, dayIndex);
        setAnalyses(results);
      } catch (error) {
        console.error("Failed to analyze all sentences:", error);
      } finally {
        setIsLoading(false);
      }
    };
    analyzeAllSentences();
  }, [story.id, dayIndex, sentences]);

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <button onClick={onGoHome} className="text-sky-600 hover:text-sky-800">&larr; 홈으로</button>
        <h1 className="text-2xl font-bold text-sky-700 text-center">{story.title} - Day {dayIndex + 1}</h1>
        <div className="w-24"></div>
      </div>
      
      {isLoading ? (
        <div className="text-center p-10">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600 mx-auto"></div>
            <p className="mt-4 text-lg text-gray-700">문장들을 분석하고 있습니다...</p>
        </div>
      ) : (
        <div>
          {sentences.map((sentence, index) => (
              <SentenceView
                  key={index}
                  sentence={sentence}
                  analysis={analyses[sentence]}
              />
          ))}
        </div>
      )}

      {!isLoading && (
        <div className="mt-8 text-center">
          <button onClick={onFinish} className="bg-blue-500 text-white font-bold py-3 px-8 rounded-lg text-lg hover:bg-blue-600 transition-colors">
            학습 완료! 퀴즈 풀기
          </button>
        </div>
      )}
    </div>
  );
};

export default LearningScreen;