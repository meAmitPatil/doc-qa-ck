"use client";

import React, { useEffect, useState } from "react";
import axios from "axios";

export default function Home() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [question, setQuestion] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [loadingAnswer, setLoadingAnswer] = useState(false);
  const [isUploaded, setIsUploaded] = useState(false);

  const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;

  // Clear Qdrant on component mount
  useEffect(() => {
    axios
      .get(`${backendUrl}/clear-qdrant`)
      .then(() => console.log("🗑️ Cleared Qdrant on refresh"))
      .catch((error) => console.error("❌ Error clearing Qdrant:", error));
  }, [backendUrl]);

  // Handle file selection
  const handleFileChange = (event) => {
    setFiles([...event.target.files]);
    setIsUploaded(false);
  };

  // Upload files to the backend
  const handleUpload = async () => {
    if (files.length === 0) {
      alert("Please select files to upload!");
      return;
    }

    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));

    try {
      setUploading(true);
      const response = await axios.post(
        `${backendUrl}/api/upload`,
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );
      console.log("Upload Response:", response.data);
      alert("Files uploaded successfully!");
      setIsUploaded(true);
    } catch (error) {
      console.error("Error uploading files:", error.response || error.message);
      alert("Failed to upload files. Please try again.");
      setIsUploaded(false);
    } finally {
      setUploading(false);
    }
  };

  // Ask a question and fetch the answer from the backend
  const handleAskQuestion = async () => {
    if (!isUploaded) {
      alert("Please upload a document first before asking questions.");
      return;
    }

    if (question.trim() === "") {
      alert("Please enter a question.");
      return;
    }

    try {
      setLoadingAnswer(true);

      const response = await axios.post(`${backendUrl}/api/qa`, { question });
      console.log("Backend Response:", response.data);

      const answer = response.data.answer;
      const sources = response.data.sources || [];

      setChatHistory((prev) => [
        ...prev,
        { type: "question", text: question },
        { type: "answer", text: answer },
        ...(sources.length > 0
          ? [
              {
                type: "sources",
                text: sources.map(
                  (source) =>
                    `${source.filename}: ${
                      source.content
                        ? source.content.substring(0, 150) + "..."
                        : "No content available"
                    }`
                ),
              },
            ]
          : []),
      ]);

      setQuestion("");
    } catch (error) {
      console.error("Error fetching answer:", error.response || error.message);
      alert("An error occurred while fetching the answer. Please try again.");
    } finally {
      setLoadingAnswer(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 flex flex-col items-center py-10 px-4">
      {/* Container with 3 columns at md size and above */}
      <div className="max-w-6xl w-full grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Left Panel: Upload Section (spans 1 column) */}
        <div className="bg-white/70 backdrop-blur-xl shadow-xl rounded-2xl p-6 md:p-8 flex flex-col justify-between md:col-span-1">
          <div>
            <div className="flex items-center space-x-3 mb-6">
              {/* Brand Icon or Logo */}
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-10 w-10 text-indigo-500"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              <h1 className="text-3xl font-bold text-gray-800 tracking-tight">
                Doc-<span className="text-indigo-500">Qa-Ck</span>
              </h1>
            </div>

            {/* Drag-and-Drop or Click to Select UI */}
            <div className="border-2 border-dashed border-gray-300 rounded-xl p-6 mb-4 transition hover:border-indigo-400">
              <label
                htmlFor="file-upload"
                className="flex flex-col items-center justify-center cursor-pointer"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-14 w-14 text-gray-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M7 16v-4m0 0V7m0 5l-2.5 2.5M7 11h10m4 0H7m10 0l-2.5-2.5m0 0L17 7m0 4v4"
                  />
                </svg>
                <span className="mt-3 text-sm text-gray-600 text-center">
                  Drag & drop your PDF files here,<br />or click to select
                </span>
                <input
                  id="file-upload"
                  type="file"
                  multiple
                  accept=".pdf"
                  className="hidden"
                  onChange={handleFileChange}
                />
              </label>
            </div>

            <p className="text-xs text-gray-500 mb-4 text-center">
              PDF files only, up to 10MB each.
            </p>

            {/* Display Selected Files */}
            {files.length > 0 && (
              <ul className="text-sm text-gray-700 mb-4 list-disc list-inside">
                {files.map((file, index) => (
                  <li key={index}>{file.name}</li>
                ))}
              </ul>
            )}
          </div>

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            disabled={uploading}
            className={`mt-4 w-full py-2 px-4 text-white rounded-xl 
              ${
                uploading
                  ? "bg-gray-400 cursor-not-allowed"
                  : "bg-indigo-500 hover:bg-indigo-600 transition-colors"
              }`}
          >
            {uploading ? "Uploading..." : "Upload Files"}
          </button>
        </div>

        {/* Right Panel: Q&A Section (spans 2 columns) */}
        <div className="bg-white/70 backdrop-blur-xl shadow-xl rounded-2xl p-6 md:p-8 flex flex-col md:col-span-2">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Ask Questions</h2>
          <div className="mb-4">
            <input
              type="text"
              placeholder="Type your question here..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              disabled={!isUploaded}
              className={`w-full p-3 border border-gray-300 rounded-xl text-black outline-none focus:border-indigo-500 transition ${
                !isUploaded && "bg-gray-100 cursor-not-allowed"
              }`}
            />
          </div>
          <button
            onClick={handleAskQuestion}
            disabled={loadingAnswer || !isUploaded}
            className={`w-full py-2 px-4 text-white rounded-xl mb-4
              ${
                loadingAnswer || !isUploaded
                  ? "bg-gray-400 cursor-not-allowed"
                  : "bg-green-600 hover:bg-green-700 transition-colors"
              }`}
          >
            {loadingAnswer ? "Fetching answer..." : "Ask Question"}
          </button>

          {/* Chat History */}
          <div
            // Set a max-height for large screens to keep chat scrollable
            className="flex-1 overflow-y-auto pr-2 max-h-[60vh] md:max-h-[70vh]"
          >
            <h3 className="text-lg font-semibold text-gray-800 mb-4 border-b border-gray-200 pb-2">
              Chat History
            </h3>
            <div className="space-y-4">
              {chatHistory.map((entry, index) => (
                <div
                  key={index}
                  className={`flex w-full ${
                    entry.type === "question" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`relative p-4 rounded-lg shadow-md max-w-sm ${
                      entry.type === "question"
                        ? "bg-indigo-100 text-indigo-900"
                        : "bg-gray-100 text-gray-800"
                    }`}
                  >
                    {entry.type === "question" && (
                      <span className="absolute -top-3 right-2 bg-indigo-600 text-white text-xs py-0.5 px-2 rounded-full">
                        Q
                      </span>
                    )}
                    {entry.type === "answer" && (
                      <span className="absolute -top-3 left-2 bg-green-600 text-white text-xs py-0.5 px-2 rounded-full">
                        A
                      </span>
                    )}
                    <div className="whitespace-pre-wrap">
                      {entry.type !== "sources" && entry.text}
                      {entry.type === "sources" && (
                        <div className="mt-2">
                          <h4 className="font-bold text-gray-800 underline">Sources:</h4>
                          <ol className="mt-2 list-decimal pl-5 text-sm space-y-1">
                            {entry.text.map((source, idx) => (
                              <li key={idx}>{source}</li>
                            ))}
                          </ol>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}