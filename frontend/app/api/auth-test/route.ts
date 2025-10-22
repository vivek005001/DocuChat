import { NextResponse } from 'next/server';
import { verifyUser } from '@/lib/verifyuser';
import { cookies } from 'next/headers';

export async function GET() {
  const userId = await verifyUser();
  const cookieStore = await cookies();
  const token = cookieStore.get('token')?.value;
  
  return NextResponse.json({
    userId,
    authenticated: !!userId,
    tokenExists: !!token,
    jwt_secret_exists: !!process.env.JWT_SECRET,
    backend_url: process.env.BACKEND_URL,
  });
}