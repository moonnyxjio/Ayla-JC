
import React from 'react';

const ApiKeyErrorScreen: React.FC = () => {
  return (
    <div className="text-center p-8 bg-red-50 border-2 border-red-200 rounded-lg">
      <h1 className="text-2xl font-bold text-red-700 mb-4">Configuration Error</h1>
      <p className="text-lg text-red-600 mb-4">
        The application is missing the required Gemini API Key.
      </p>
      <p className="text-md text-gray-700">
        This app is designed to run in an environment where the <code>API_KEY</code> is provided as an environment variable. If you are deploying this on a platform like Vercel, please make sure you have set the <code>API_KEY</code> in your project's settings.
      </p>
      <div className="mt-6 flex flex-col sm:flex-row justify-center items-center gap-4">
        <a href="https://ai.google.dev/gemini-api/docs/api-key" target="_blank" rel="noopener noreferrer" className="inline-block bg-gray-500 text-white font-bold py-2 px-4 rounded-lg hover:bg-gray-600 transition-colors">
          Get an API Key
        </a>
        <a href="https://vercel.com/docs/projects/environment-variables" target="_blank" rel="noopener noreferrer" className="inline-block bg-blue-500 text-white font-bold py-2 px-4 rounded-lg hover:bg-blue-600 transition-colors">
          How to set Env Vars on Vercel
        </a>
      </div>
    </div>
  );
};

export default ApiKeyErrorScreen;
