import { NextResponse } from "next/server";
import { connectDB } from "@/lib/dbconnect"; 
import User from "@/models/User";
import { generateToken, setAuthCookie } from "@/lib/auth";

export async function POST(req: Request) {
  try {
    await connectDB();
    const { email, password } = await req.json();

    const user = await User.findOne({ email });
    if (!user || !(await user.matchPassword(password)))
      return NextResponse.json({ message: "Invalid credentials" }, { status: 401 });

    const token = generateToken(String(user._id));
  await setAuthCookie(token);

    return NextResponse.json(
      { id: user._id, name: user.name, email: user.email },
      { status: 200 }
    );
  } catch (err: any) {
    return NextResponse.json({ message: err.message }, { status: 500 });
  }
}
