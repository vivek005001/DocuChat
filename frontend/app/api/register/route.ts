import { NextResponse } from "next/server";
import { connectDB } from "@/lib/dbconnect";
import User from "@/models/User";
import { generateToken, setAuthCookie } from "@/lib/auth";

export async function POST(req: Request) {
  try {
    await connectDB();
    const { name, email, password } = await req.json();
    console.log(name, email, password);
    const exists = await User.findOne({ email });
    if (exists) return NextResponse.json({ message: "User exists" }, { status: 400 });

    const user = await User.create({ name, email, password });
    const token = generateToken(String(user._id));
    // ensure the auth cookie is set before returning the response
    await setAuthCookie(token);

    return NextResponse.json(
      { id: user._id, name: user.name, email: user.email },
      { status: 201 }
    );
  } catch (err: any) {
    return NextResponse.json({ message: err.message }, { status: 500 });
  }
}

// Provide a helpful response for browser GET requests (instead of the default blank 405)
export function GET() {
  return NextResponse.json(
    { message: "Method Not Allowed. Use POST to register." },
    { status: 405 }
  );
}
