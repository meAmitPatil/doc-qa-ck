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

  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/clear-qdrant")
      .then(() => console.log("🗑️ Cleared Qdrant on refresh"))
      .catch((error) => console.error("❌ Error clearing Qdrant:", error));
  }, []);

  const handleFileChange = (event) => {
    setFiles([...event.target.files]);
    setIsUploaded(false);
  };

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
      setIsUploaded(true);
    } catch (error) {
      setIsUploaded(false);
      console.error("Error uploading files:", error);
      alert("Failed to upload files. Please try again.");
    } finally {
      setUploading(false);
    }
  };

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
      const sources = response.data.sources || [];

      const hasSources = sources.length > 0;

      setChatHistory((prev) => [
        ...prev,
        { type: "question", text: question },
        { type: "answer", text: answer },
        ...(hasSources
          ? [
              {
                type: "sources",
                text: sources.map(
                  (source) =>
                    `${source.filename}: ${source.content?.substring(0, 150) || "Content not available"}...`
                ),
              },
            ]
          : []),
      ]);

      setQuestion("");
    } catch (error) {
      console.error("Error fetching answer:", error);
      alert("An error occurred while fetching the answer.");
    } finally {
      setLoadingAnswer(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
      <div className="max-w-2xl w-full bg-white shadow-lg rounded-lg p-6 mb-6">
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

      <div className="max-w-2xl w-full bg-white shadow-lg rounded-lg p-6">
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
              <div
                key={index}
                className={`flex ${
                  entry.type === "question" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`p-4 rounded-lg shadow-md ${
                    entry.type === "question" ? "bg-blue-200 text-black" : "bg-gray-200 text-black"
                  }`}
                >
                  {entry.type === "question" && <strong>Q:</strong>}{" "}
                  {entry.type === "answer" && <strong>A:</strong>}{" "}
                  {entry.type !== "sources" && entry.text}
                  {entry.type === "sources" && (
                    <div className="mt-2">
                      <h4 className="font-bold text-gray-800">Sources:</h4>
                      <ol className="mt-2 list-decimal pl-5 text-sm">
                        {entry.text.map((source, idx) => (
                          <li key={idx}>{source}</li>
                        ))}
                      </ol>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
