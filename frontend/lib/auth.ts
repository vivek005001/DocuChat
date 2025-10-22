import jwt from "jsonwebtoken";
import { cookies } from "next/headers";

const JWT_SECRET = process.env.JWT_SECRET as string;

export function generateToken(id: string) {
  return jwt.sign({ id }, JWT_SECRET, { expiresIn: "7d" });
}

export async function setAuthCookie(token: string) {
  try {
    // cookies() can be a Promise<ReadonlyRequestCookies> in this environment,
    // so await it and cast to any to access .set for response cookies.
    const cookieStore = (await cookies()) as any;
    cookieStore.set("token", token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      maxAge: 7 * 24 * 60 * 60,
      path: "/",
    });
    console.log("Auth cookie set successfully");
  } catch (error) {
    console.error("Error setting auth cookie:", error);
    throw error;
  }
}
