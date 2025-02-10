import { useState } from 'react';
import axios from 'axios';

//post user's canvas API key to the backend
export const postApiKey = async (ApiKey: string) => {
  const response = await axios.post('http://localhost:8000/token/', ApiKey);
  return response.data;
};

export const ApiUpload = () => {
  const [apiKey, setApiKey] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!apiKey) return;
    //apiKey validation logic here
    const result = await postApiKey(apiKey);
    const jwt_token = result.access_token;
    console.log(result);
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 px-4">
      <div className="bg-white shadow-lg rounded-2xl p-8 w-full max-w-md">
        {/* Header */}
        <h2 className="text-2xl font-bold text-gray-900 text-center mb-6">
          Learn 10X Faster With CanvasLM
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-gray-700 text-sm font-medium mb-2">
              canvas API Key
            </label>
            <input
              className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              type="string"
              onChange={(e) => {
                const value = e.target.value.trim(); // Trim to remove unnecessary spaces
                setApiKey(value.length > 0 ? value : null);
              }}
            ></input>
            <div className="mb-2 mt-2"></div>
            <button
              className="w-full bg-orange-500 hover:bg-orange-600 text-white font-semibold py-2 rounded-lg transition duration-300"
              type="submit"
            >
              Go to CanvasLM
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
