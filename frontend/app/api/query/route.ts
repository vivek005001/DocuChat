import { NextRequest, NextResponse } from "next/server";
import { verifyUser } from "@/lib/verifyuser";
import { cookies } from "next/headers";

// Debug user ID - a valid MongoDB ObjectId format (24 hex characters)
const DEBUG_USER_ID = "000000000000000000000001";

export async function POST(req: NextRequest) {
  const userId = await verifyUser();
  
  // TEMPORARY: Bypass auth check for debugging
  // if (!userId)
  //   return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
  
  // Use a debug user ID if no user is authenticated
  const effectiveUserId = userId || DEBUG_USER_ID;
  console.log("POST /api/query - Using user ID:", effectiveUserId);

  try {
    const body = await req.json();
    
    if (!body.query) {
      return NextResponse.json(
        { error: "Query is required" },
        { status: 400 }
      );
    }
    
    // Build the request to the backend
    const requestData: { 
      query: string; 
      doc_id?: string;
    } = {
      query: body.query,
    };
    
    // Add document filter if provided
    if (body.documentId) {
      // For the backend, we need to get the vector ID from document ID
      requestData.doc_id = body.documentId;
    }
    
    const cookieStore = await cookies();
    const token = cookieStore.get("token")?.value || "debug-token"; // Fallback to debug token
    
    console.log("Query - BACKEND_URL:", process.env.BACKEND_URL);
    console.log("Query - Auth token exists:", !!token);
    
    const response = await fetch(`${process.env.BACKEND_URL}/api/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.detail || "Failed to process query" },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error processing query:", error);
    return NextResponse.json(
      { error: "Failed to process query" },
      { status: 500 }
    );
  }
}