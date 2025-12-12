/**
 * Test Better Auth signup and signin
 */

async function testAuth() {
  const baseUrl = 'http://localhost:3000';

  console.log('🧪 Testing Better Auth...\n');

  // Test 1: Sign up a new user
  console.log('1️⃣ Testing signup...');
  try {
    const signupResponse = await fetch(`${baseUrl}/api/auth/sign-up/email`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'newuser@example.com',
        password: 'testpass123',
        name: 'New User',
      }),
    });

    if (signupResponse.ok) {
      const signupData = await signupResponse.json();
      console.log('✅ Signup successful:', signupData.user.email);
    } else {
      const error = await signupResponse.text();
      console.log('❌ Signup failed:', error);
    }
  } catch (error) {
    console.log('❌ Signup error:', error);
  }

  // Test 2: Sign in with the user
  console.log('\n2️⃣ Testing signin...');
  try {
    const signinResponse = await fetch(`${baseUrl}/api/auth/sign-in/email`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'testuser@example.com',
        password: 'testpass123',
      }),
    });

    if (signinResponse.ok) {
      const signinData = await signinResponse.json();
      console.log('✅ Signin successful:', signinData.user.email);
    } else {
      const error = await signinResponse.text();
      console.log('❌ Signin failed:', error);
    }
  } catch (error) {
    console.log('❌ Signin error:', error);
  }

  console.log('\n✨ Auth tests complete!');
}

testAuth();
