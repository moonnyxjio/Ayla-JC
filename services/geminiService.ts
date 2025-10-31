
import { GoogleGenAI, Modality, Type } from '@google/genai';
import type { SentenceAnalysisData, WordAnalyses } from '../types';

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY as string });

// Shortened the list to analyze more words, as requested.
const EXCLUDED_WORDS_LIST = ['a', 'an', 'the'];


export const analyzeSentencesForDay = async (sentences: string[], storyId: string, dayIndex: number): Promise<Record<string, SentenceAnalysisData>> => {
    const cacheKey = `analysis-day-v5-${storyId}-${dayIndex}`; // v5 for english pronunciation jamo
    try {
        const cachedData = sessionStorage.getItem(cacheKey);
        if (cachedData) {
            return JSON.parse(cachedData);
        }
    } catch (e) {
        console.error("Could not read from session cache", e);
    }

    try {
        const sentencesObjectForPrompt = sentences.map((sentence, index) => {
            const wordsInSentence = [...new Set(sentence.replace(/[.,?!"]/g, '').toLowerCase().split(' ').filter(word => word && !EXCLUDED_WORDS_LIST.includes(word)))];
            return `{ "id": ${index}, "sentence": "${sentence.replace(/"/g, '\\"')}", "wordsToAnalyze": ["${wordsInSentence.join('", "')}"] }`;
        }).join(',\n');
        
        const prompt = `For the following array of English sentences, provide a JSON object as a response. The key for each entry in the root object should be the original sentence string. The value for each key should be another JSON object with two keys: "chunkedTranslation" and "wordAnalyses".
1. "chunkedTranslation": A Korean translation of the sentence, broken into meaningful chunks separated by " / ".
2. "wordAnalyses": A JSON object where keys are the important English words from that sentence and values are objects containing their "koreanMeaning" and "phonics". The "phonics" must represent the pronunciation of the **English word** using Hangul Jamo characters. For example, for "school" it should be "ㅅㅋㅜ~ㄹ", for "pick" it should be "ㅍㅣㅋ", and for "guess" it should be "ㄱㅔㅅㅅ".

Analyze the words provided in the 'wordsToAnalyze' array for each sentence.

Sentences to analyze:
[
${sentencesObjectForPrompt}
]

Example response format:
{
  "A robot is in the box.": {
    "chunkedTranslation": "하나의 로봇이 / 상자 안에 있어요.",
    "wordAnalyses": {
      "robot": { "koreanMeaning": "로봇", "phonics": "ㄹㅗㅂㅏㅌ" },
      "box": { "koreanMeaning": "상자", "phonics": "ㅂㅏㄱㅅ" }
    }
  },
  "I see a box.": {
     "chunkedTranslation": "나는 / 상자를 본다.",
     "wordAnalyses": {
        "see": { "koreanMeaning": "보다", "phonics": "ㅆㅣ" },
        "box": { "koreanMeaning": "상자", "phonics": "ㅂㅏㄱㅅ" }
     }
  }
}
`;

        const response = await ai.models.generateContent({
            model: 'gemini-2.5-flash',
            contents: prompt,
            config: {
                responseMimeType: 'application/json',
            },
        });
        
        const jsonString = response.text.trim();
        const result = JSON.parse(jsonString) as Record<string, SentenceAnalysisData>;
        
        try {
            sessionStorage.setItem(cacheKey, JSON.stringify(result));
        } catch (e) {
            console.error("Could not write to session cache", e);
        }

        return result;

    } catch (error) {
        console.error("Error fetching batch sentence analysis:", error);
        const errorResult: Record<string, SentenceAnalysisData> = {};
        sentences.forEach(sentence => {
            errorResult[sentence] = {
                chunkedTranslation: "번역을 가져오는 데 실패했습니다.",
                wordAnalyses: {}
            };
            const words = [...new Set(sentence.replace(/[.,?!"]/g, '').toLowerCase().split(' ').filter(word => word && !EXCLUDED_WORDS_LIST.includes(word)))];
            words.forEach(word => {
                if (word) {
                    errorResult[sentence].wordAnalyses[word] = {
                        koreanMeaning: "분석 실패",
                        phonics: "분석 실패"
                    };
                }
            });
        });
        return errorResult;
    }
};


export const getSpeech = async (text: string): Promise<string | null> => {
    try {
        const response = await ai.models.generateContent({
            model: "gemini-2.5-flash-preview-tts",
            contents: [{ parts: [{ text: text }] }],
            config: {
                responseModalities: [Modality.AUDIO],
                speechConfig: {
                    voiceConfig: {
                        prebuiltVoiceConfig: { voiceName: 'Kore' },
                    },
                },
            },
        });

        const base64Audio = response.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data;
        if (base64Audio) {
            return base64Audio;
        }
        return null;
    } catch (error)
 {
        console.error("Error generating speech:", error);
        return null;
    }
};