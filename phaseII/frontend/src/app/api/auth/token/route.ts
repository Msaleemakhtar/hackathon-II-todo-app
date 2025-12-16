import { NextRequest, NextResponse } from 'next/server';
import { getAuth } from '@/lib/auth-server';
import * as jose from 'jose';

/**
 * Custom endpoint to generate JWT tokens for Better Auth sessions
 *
 * This endpoint:
 * 1. Validates the Better Auth session
 * 2. Generates a JWT token with the same structure expected by FastAPI backend
 * 3. Returns the JWT token that can be used for API requests
 */
export async function GET(request: NextRequest) {
  try {
    // Get the auth instance (this will initialize it at runtime if not already done)
    const auth = getAuth();

    // Get the session from Better Auth
    const session = await auth.api.getSession({
      headers: request.headers,
    });

    // If no session, return 401
    if (!session || !session.user) {
      return NextResponse.json(
        { error: 'Not authenticated' },
        { status: 401 }
      );
    }

    // Create JWT payload matching the structure expected by FastAPI
    const payload = {
      sub: session.user.id,        // User ID
      email: session.user.email,   // User email
      name: session.user.name,     // User name (optional)
      exp: Math.floor(Date.now() / 1000) + (30 * 60), // 30 minutes expiry (max in 15-30 range)
      iat: Math.floor(Date.now() / 1000), // Issued at
      type: 'access', // Token type
    };

    // Sign the JWT with BETTER_AUTH_SECRET (same secret as backend)
    const secret = new TextEncoder().encode(process.env.BETTER_AUTH_SECRET!);
    const token = await new jose.SignJWT(payload)
      .setProtectedHeader({ alg: 'HS256' })
      .setIssuedAt()
      .setExpirationTime('30m')  // Set to 30 minutes to meet backend validation requirements
      .sign(secret);

    // Return the JWT token
    return NextResponse.json({
      token,
      user: {
        id: session.user.id,
        email: session.user.email,
        name: session.user.name,
      },
      expiresAt: payload.exp,
    });
  } catch (error) {
    console.error('Error generating JWT token:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
