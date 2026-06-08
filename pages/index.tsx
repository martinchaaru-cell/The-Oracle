import React from 'react';

export default function Index() {
  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>🎯 Match Oracle</h1>
      <p>Welcome to the Match Oracle platform</p>
      <p>Your AI-powered football prediction system</p>
      <hr />
      <h2>Status: ✅ Online</h2>
      <p>Frontend successfully deployed to Vercel</p>
      <p>Backend API: {process.env.NEXT_PUBLIC_API_URL || 'Not configured'}</p>
    </div>
  );
}
