import { NextResponse, NextRequest } from "next/server";
import { verifyUser } from "@/lib/verifyuser";
import { connectDB } from "@/lib/dbconnect";
import Document from "@/models/Document";
import { cookies } from "next/headers";

// Debug user ID - a valid MongoDB ObjectId format (24 hex characters)
const DEBUG_USER_ID = "000000000000000000000001";

export async function GET() {
  const userId = await verifyUser();
  
  // TEMPORARY: Bypass auth check for debugging
  // if (!userId)
  //   return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
  
  // Use a debug user ID if no user is authenticated
  const effectiveUserId = userId || DEBUG_USER_ID;
  console.log("GET /api/documents - Using user ID:", effectiveUserId);

  try {
    await connectDB();
    const docs = await Document.find({ user: effectiveUserId }).sort({ createdAt: -1 });

    // Also fetch documents from the backend vector store
    const cookieStore = await cookies();
    const token = cookieStore.get("token")?.value || "debug-token"; // Fallback to debug token
    
    console.log("BACKEND_URL:", process.env.BACKEND_URL);
    console.log("Auth token exists:", !!token);
    
    // For development purposes - always use a debug token if needed
    const debugToken = "debug-token";
    
    const response = await fetch(`${process.env.BACKEND_URL}/api/documents`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token || debugToken}`
      },
    });
    
    console.log("Backend response status:", response.status);

    if (response.ok) {
      const vectorDocs = await response.json();
      
      // Merge vector store document info with MongoDB document records
      const enrichedDocs = docs.map(doc => {
        const vectorDoc = vectorDocs.find(vd => vd.doc_id === doc.vectorId);
        return {
          ...doc.toObject(),
          chunks: vectorDoc?.chunks || 0,
          inVectorStore: Boolean(vectorDoc)
        };
      });
      
      return NextResponse.json(enrichedDocs);
    }
    
    // Fallback to just MongoDB docs if backend is unavailable
    return NextResponse.json(docs);
  } catch (error) {
    console.error("Error fetching documents:", error);
    return NextResponse.json(
      { error: "Failed to fetch documents" }, 
      { status: 500 }
    );
  }
}

export async function DELETE(req: NextRequest) {
  const userId = await verifyUser();
  
  // TEMPORARY: Bypass auth check for debugging
  // if (!userId)
  //   return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
  
  // Use a debug user ID if no user is authenticated
  const effectiveUserId = userId || DEBUG_USER_ID;
  console.log("DELETE /api/documents - Using user ID:", effectiveUserId);

  try {
    const { searchParams } = new URL(req.url);
    const docId = searchParams.get("id");
    
    if (!docId) {
      return NextResponse.json(
        { error: "Document ID is required" },
        { status: 400 }
      );
    }

    // Find document to get its vector ID
    await connectDB();
    const doc = await Document.findOne({ _id: docId, user: effectiveUserId });
    
    if (!doc) {
      return NextResponse.json(
        { error: "Document not found" },
        { status: 404 }
      );
    }
    
    // Delete from MongoDB
    await Document.deleteOne({ _id: docId, user: effectiveUserId });
    
    // Delete from vector store if we have a vectorId
    if (doc.vectorId) {
      const cookieStore = await cookies();
      const token = cookieStore.get("token")?.value || "";
      
      const backendResponse = await fetch(`${process.env.BACKEND_URL}/api/documents/${doc.vectorId}`, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
      });
      
      // Still consider the operation successful if MongoDB delete worked
      // but log any issues with vector store deletion
      if (!backendResponse.ok) {
        console.error("Failed to delete from vector store:", docId, doc.vectorId);
      }
    }

    return NextResponse.json({ message: "Document deleted successfully" });
  } catch (error) {
    console.error("Error deleting document:", error);
    return NextResponse.json(
      { error: "Failed to delete document" },
      { status: 500 }
    );
  }
}
