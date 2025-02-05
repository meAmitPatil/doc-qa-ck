"use client";

import React, { useState } from "react";
import axios from "axios";

export default function Home() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);

  // Handle file selection
  const handleFileChange = (event) => {
    setFiles([...event.target.files]);
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
          withCredentials: true, // Ensures cookies are sent with the request
        }
      );
      alert("Files uploaded successfully!");
      console.log(response.data);
    } catch (error) {
      // Enhanced error handling
      if (error.response) {
        // Server responded with a status other than 2xx
        console.error("Response error:", error.response.data);
        alert(`Failed to upload files: ${error.response.data.detail || "Unknown error"}`);
      } else if (error.request) {
        // Request was made but no response was received
        console.error("Request error:", error.request);
        alert("No response received from the server. Check your backend.");
      } else {
        // Other errors
        console.error("Error:", error.message);
        alert("An error occurred: " + error.message);
      }
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full bg-white shadow-md rounded-lg p-6">
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
            <span className="mt-2 text-sm text-gray-600">Drag & drop your PDF files here, or click to select</span>
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
    </div>
  );
}
