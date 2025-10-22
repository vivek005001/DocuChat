"use client";
import { useState, useEffect } from "react";
import axios from "axios";

type Document = {
  _id: string;
  filename: string;
  mimetype: string;
  createdAt: string;
  vectorId?: string;
  chunks?: number;
  inVectorStore?: boolean;
};

type ChatMessage = {
  role: 'user' | 'assistant';
  content: string;
};

export default function Dashboard() {
  const [file, setFile] = useState<File | null>(null);
  const [docs, setDocs] = useState<Document[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [uploadLoading, setUploadLoading] = useState<boolean>(false);
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
  const [query, setQuery] = useState<string>("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [queryLoading, setQueryLoading] = useState<boolean>(false);

  useEffect(() => {
    fetchDocs();
  }, []);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return alert("Please select a file");

    setUploadLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await axios.post("/api/upload", formData);
      setFile(null);
      fetchDocs();
      
      if (response.data.chunks) {
        alert(`File uploaded and processed with ${response.data.chunks} chunks!`);
      } else {
        alert("File uploaded but processing may have failed. Check documents list.");
      }
    } catch (error) {
      console.error("Upload error:", error);
      alert("Upload failed. Please try again.");
    } finally {
      setUploadLoading(false);
    }
  };

  const fetchDocs = async () => {
    setLoading(true);
    try {
      // Add debug bypass header in development environment
      const headers = process.env.NODE_ENV === 'development' 
        ? { 'x-bypass-auth': 'true' } 
        : {};
        
      const { data } = await axios.get("/api/documents", { headers });
      setDocs(data);
    } catch (error) {
      console.error("Error fetching documents:", error);
      alert("Failed to fetch documents.");
    } finally {
      setLoading(false);
    }
  };

  const deleteDocument = async (docId: string) => {
    if (!confirm("Are you sure you want to delete this document?")) {
      return;
    }
    
    setLoading(true);
    try {
      await axios.delete(`/api/documents?id=${docId}`);
      fetchDocs();
      
      if (selectedDoc?._id === docId) {
        setSelectedDoc(null);
        setMessages([]);
      }
    } catch (error) {
      console.error("Error deleting document:", error);
      alert("Failed to delete document.");
    } finally {
      setLoading(false);
    }
  };

  const handleQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    // Add user message
    const userMessage: ChatMessage = {
      role: 'user',
      content: query
    };
    setMessages(prev => [...prev, userMessage]);
    setQueryLoading(true);
    
    try {
      const requestData: { query: string; documentId?: string } = {
        query: query
      };
      
      // Add document filter if a document is selected
      if (selectedDoc?.vectorId) {
        requestData.documentId = selectedDoc.vectorId;
      }
      
      const response = await axios.post('/api/query', requestData);
      
      // Add assistant response
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.data.answer || "Sorry, I couldn't find an answer."
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      setQuery("");
    } catch (error) {
      console.error("Query error:", error);
      
      // Add error message
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: "Sorry, there was an error processing your query."
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setQueryLoading(false);
    }
  };

  return (
    <div className="p-6 flex flex-col md:flex-row h-screen gap-6 bg-[#202123] text-[#d1d5db]">
      {/* Left sidebar - Documents */}
      <div className="md:w-1/4 p-4 border rounded-lg bg-[#1e293b] overflow-y-auto">
        <h2 className="text-xl font-bold mb-4">📄 Documents</h2>
        
        <form onSubmit={handleUpload} className="mb-4 space-y-2">
          <input
            type="file"
            accept=".pdf,.txt"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="w-full bg-[#2d3748] text-[#d1d5db] border border-[#10a37f] rounded"
          />
          <button
            type="submit"
            disabled={uploadLoading || !file}
            className="bg-[#10a37f] text-[#d1d5db] px-3 py-1 rounded w-full disabled:bg-[#4a5568]"
          >
            {uploadLoading ? "Uploading..." : "Upload"}
          </button>
        </form>
        
        <div className="flex justify-between items-center mt-6 mb-2">
          <h3 className="text-lg font-semibold">My Documents</h3>
          <button
            onClick={fetchDocs}
            disabled={loading}
            className="text-sm bg-[#2d3748] px-2 py-1 rounded"
          >
            {loading ? "..." : "↻"}
          </button>
        </div>
        
        {loading ? (
          <p className="text-[#a0aec0]">Loading documents...</p>
        ) : docs.length === 0 ? (
          <p className="text-[#a0aec0]">No documents found. Upload one to get started!</p>
        ) : (
          <ul className="space-y-2">
            <li
              onClick={() => {
                setSelectedDoc(null);
                setMessages([]);
              }}
              className={`p-2 rounded cursor-pointer hover:bg-[#2d3748] ${
                !selectedDoc ? "bg-[#10a37f] border-[#10a37f] border" : ""
              }`}
            >
              <div className="font-medium">All Documents</div>
              <div className="text-xs text-[#a0aec0]">
                Query across all documents
              </div>
            </li>
            
            {docs.map((doc) => (
              <li
                key={doc._id}
                onClick={() => {
                  setSelectedDoc(doc);
                  setMessages([]);
                }}
                className={`p-2 rounded cursor-pointer hover:bg-[#2d3748] ${
                  selectedDoc?._id === doc._id ? "bg-[#10a37f] border-[#10a37f] border" : ""
                }`}
              >
                <div className="flex justify-between">
                  <span className="font-medium truncate">{doc.filename}</span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteDocument(doc._id);
                    }}
                    className="text-red-500 hover:text-red-700 text-sm"
                  >
                    ×
                  </button>
                </div>
                <div className="text-xs text-[#a0aec0]">
                  {new Date(doc.createdAt).toLocaleDateString()}
                </div>
                {doc.chunks !== undefined && (
                  <div className="text-xs text-[#a0aec0]">
                    {doc.chunks} chunks{!doc.inVectorStore && " (not in vector store)"}
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
      
      {/* Right side - Chat */}
      <div className="flex-1 flex flex-col h-full border rounded-lg overflow-hidden bg-[#1e293b]">
        <div className="p-4 border-b bg-[#2d3748]">
          <h2 className="text-xl font-semibold">
            💬 Chat with {selectedDoc ? selectedDoc.filename : "All Documents"}
          </h2>
        </div>
        
        <div className="flex-1 p-4 overflow-y-auto bg-[#202123]">
          {messages.length === 0 ? (
            <div className="text-center text-[#a0aec0] mt-10">
              <p>Ask a question about {selectedDoc ? "this document" : "your documents"}!</p>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`p-3 rounded-lg ${
                    msg.role === "user"
                      ? "bg-[#10a37f] ml-10"
                      : "bg-[#2d3748] mr-10 shadow-sm"
                  }`}
                >
                  {msg.content}
                </div>
              ))}
              {queryLoading && (
                <div className="bg-[#2d3748] p-3 rounded-lg mr-10 shadow-sm">
                  <div className="animate-pulse">Thinking...</div>
                </div>
              )}
            </div>
          )}
        </div>
        
        <div className="p-4 border-t bg-[#2d3748]">
          <form onSubmit={handleQuery} className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a question..."
              className="flex-1 p-2 border rounded bg-[#1e293b] text-[#d1d5db]"
              disabled={queryLoading}
            />
            <button
              type="submit"
              disabled={queryLoading || !query.trim()}
              className="bg-[#10a37f] text-[#d1d5db] px-4 py-2 rounded disabled:bg-[#4a5568]"
            >
              {queryLoading ? "..." : "Ask"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
