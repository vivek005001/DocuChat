import { NextRequest, NextResponse } from "next/server";

// This middleware runs before your API routes
export async function middleware(request: NextRequest) {
  // Only bypass auth in development
  if (process.env.NODE_ENV === 'development') {
    // Check for our special bypass header
    const bypassAuth = request.headers.get('x-bypass-auth');
    
    if (bypassAuth === 'true') {
      // Add a debug token header that the backend will recognize
      const response = NextResponse.next();
      response.headers.set('Authorization', 'Bearer debug-token');
      return response;
    }
  }
  
  // For all other requests, continue normal flow
  return NextResponse.next();
}

// Apply this middleware only to API routes
export const config = {
  matcher: '/api/:path*',
};