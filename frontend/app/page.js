"use client";

import React, { useEffect, useState } from "react";
import axios from "axios";

export default function Home() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [question, setQuestion] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [loadingAnswer, setLoadingAnswer] = useState(false);
  const [isUploaded, setIsUploaded] = useState(false); // Track if files are uploaded

  useEffect(() => {
    axios.get("http://127.0.0.1:8000/clear-qdrant")
      .then(() => console.log("🗑️ Cleared Qdrant on refresh"))
      .catch((error) => console.error("❌ Error clearing Qdrant:", error));
  }, []);

  // Handle file selection
  const handleFileChange = (event) => {
    setFiles([...event.target.files]);
    setIsUploaded(false); // Reset upload status when new files are selected
  };

  // Handle file upload
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
        "http://127.0.0.1:8000/api/upload",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
          withCredentials: true,
        }
      );
      alert("Files uploaded successfully!");
      console.log(response.data);
      setIsUploaded(true); // Mark upload as successful
    } catch (error) {
      setIsUploaded(false); // Mark upload as failed
      if (error.response) {
        console.error("Response error:", error.response.data);
        alert(`Failed to upload files: ${error.response.data.detail || "Unknown error"}`);
      } else if (error.request) {
        console.error("Request error:", error.request);
        alert("No response received from the server. Check your backend.");
      } else {
        console.error("Error:", error.message);
        alert("An error occurred: " + error.message);
      }
    } finally {
      setUploading(false);
    }
  };

  // Handle asking a question
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
      const response = await axios.post("http://127.0.0.1:8000/api/qa", { question });

      const answer = response.data.answer;
      const sources = response.data.sources || []; // Ensure sources is always an array

      // Only include sources if Qdrant was used
      const hasSources = sources.length > 0;

      setChatHistory((prev) => [
        ...prev,
        { type: "question", text: question },
        { type: "answer", text: answer },
        ...(hasSources ? [{ type: "sources", text: sources }] : []), // ✅ Only add if sources exist
      ]);

      setQuestion(""); // Clear the input field
    } catch (error) {
      console.error("Error fetching answer:", error);
      alert("An error occurred while fetching the answer.");
    } finally {
      setLoadingAnswer(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      <div className="max-w-2xl w-full bg-white shadow-md rounded-lg p-6 mb-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">DOC-QA-CK</h1>
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 mb-4">
          <label
            htmlFor="file-upload"
            className="flex flex-col items-center justify-center cursor-pointer"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-12 w-12 text-gray-400"
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
            <span className="mt-2 text-sm text-gray-600">
              Drag & drop your PDF files here, or click to select
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
        <p className="text-sm text-gray-500 mb-4">PDF files only, up to 10MB each.</p>

        {files.length > 0 && (
          <ul className="text-sm text-gray-600 mb-4">
            {files.map((file, index) => (
              <li key={index}>{file.name}</li>
            ))}
          </ul>
        )}

        <button
          onClick={handleUpload}
          disabled={uploading}
          className={`w-full py-2 px-4 text-white rounded-lg ${
            uploading ? "bg-gray-400" : "bg-blue-600 hover:bg-blue-700"
          }`}
        >
          {uploading ? "Uploading..." : "Upload Files"}
        </button>
      </div>

      <div className="max-w-2xl w-full bg-white shadow-md rounded-lg p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Ask Questions</h2>
        <div className="mb-4">
          <input
            type="text"
            placeholder="Type your question here..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            disabled={!isUploaded}
            className={`w-full p-2 border ${
              isUploaded ? "border-gray-300" : "border-gray-300 bg-gray-100 cursor-not-allowed"
            } rounded-lg text-black`}
          />
        </div>
        <button
          onClick={handleAskQuestion}
          disabled={loadingAnswer || !isUploaded}
          className={`w-full py-2 px-4 text-white rounded-lg ${
            loadingAnswer || !isUploaded
              ? "bg-gray-400 cursor-not-allowed"
              : "bg-green-600 hover:bg-green-700"
          }`}
        >
          {loadingAnswer ? "Fetching answer..." : "Ask Question"}
        </button>

        <div className="mt-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Chat History</h3>
          <div className="space-y-4">
            {chatHistory.map((entry, index) => (
              <div key={index} className="p-4 rounded-lg shadow-md bg-white">
                {entry.type === "question" && (
                  <div className="font-bold text-blue-600">
                    Q: {entry.text}
                  </div>
                )}
                {entry.type === "answer" && (
                  <div className="text-gray-800">
                    A: {entry.text}
                  </div>
                )}
                {entry.type === "sources" && entry.text.length > 0 && (
                  <div className="text-gray-600">
                    <strong>Sources:</strong>
                    <ul className="list-disc pl-5">
                      {entry.text.map((source, idx) => (
                        <li key={idx}>
                          <strong>{source.filename}</strong>: {source.content?.substring(0, 100) || "Content not available."}...
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
