import { NextResponse } from "next/server";
import { connectDB } from "@/lib/dbconnect";
import { verifyUser } from "@/lib/verifyuser";
import Document from "@/models/Document";
import { cookies } from "next/headers";
import path from "path";
import fs from "fs";
import { writeFile } from "fs/promises";

// Debug user ID - a valid MongoDB ObjectId format (24 hex characters)
const DEBUG_USER_ID = "000000000000000000000001";

const uploadDir = path.join(process.cwd(), "uploads");
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir, { recursive: true });

export async function POST(req: Request) {
  const userId = await verifyUser();
  
  // TEMPORARY: Bypass auth check for debugging
  // if (!userId)
  //   return NextResponse.json({ message: "Unauthorized" }, { status: 401 });
  
  // Use a debug user ID if no user is authenticated
  const effectiveUserId = userId || DEBUG_USER_ID;
  console.log("POST /api/upload - Using user ID:", effectiveUserId);

  await connectDB();

  try {
    const formData = await req.formData();
    const file = formData.get("file") as File;
    
    if (!file) {
      return NextResponse.json({ message: "No file provided" }, { status: 400 });
    }

    // Generate unique filename
    const filename = Date.now() + "-" + file.name;
    const filepath = path.join(uploadDir, filename);

    // Convert file to buffer and save
    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);
    await writeFile(filepath, buffer);

    // Create document in MongoDB
    const doc = await Document.create({
      user: effectiveUserId,
      filename: file.name,
      filepath: filepath,
      mimetype: file.type,
    });

    // Process document with backend
    const backendFormData = new FormData();
    const fileBlob = new Blob([buffer], { type: file.type });
    backendFormData.append("file", fileBlob, file.name);

    const cookieStore = await cookies();
    const token = cookieStore.get("token")?.value || "debug-token"; // Fallback to debug token
    
    console.log("Upload - BACKEND_URL:", process.env.BACKEND_URL);
    console.log("Upload - Auth token exists:", !!token);
    
    const backendResponse = await fetch(`${process.env.BACKEND_URL}/api/ingest`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`
      },
      body: backendFormData,
    });

    if (backendResponse.ok) {
      const backendData = await backendResponse.json();
      
      // Update document with vector ID for future reference
      if (backendData.doc_id) {
        await Document.findByIdAndUpdate(doc._id, {
          vectorId: backendData.doc_id,
        });
        
        doc.vectorId = backendData.doc_id;
      }
      
      return NextResponse.json({
        message: "File uploaded and processed",
        document: doc,
        chunks: backendData.chunks || 0,
      }, { status: 201 });
    } else {
      // Document still created in MongoDB, even if backend processing failed
      console.error("Backend processing failed:", await backendResponse.text());
      return NextResponse.json({
        message: "File uploaded but processing failed",
        document: doc,
      }, { status: 201 });
    }
  } catch (error) {
    console.error("Error in file upload:", error);
    return NextResponse.json({ message: "Error processing file" }, { status: 500 });
  }
}
