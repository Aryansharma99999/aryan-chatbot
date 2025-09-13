

import './App.css';

import Chatbot from './Chatbot';
import { useEffect, useState } from 'react';

function App() {
  const welcomeText = "Welcome to my personal website!";
  const [typedText, setTypedText] = useState("");

  useEffect(() => {
    let i = 0;
    setTypedText("");
    const interval = setInterval(() => {
      setTypedText((prev) => prev + welcomeText[i]);
      i++;
      if (i >= welcomeText.length) clearInterval(interval);
    }, 80);
    return () => clearInterval(interval);
  }, []);

  return (
    <div
      style={{
        minHeight: '100vh',
        width: '100vw',
        position: 'fixed',
        top: 0,
        left: 0,
        background: 'linear-gradient(135deg, #ff6ec4 0%, #7873f5 100%)',
        color: '#f5f6fa',
        fontFamily: 'Inter, Arial, sans-serif',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 0,
        zIndex: 0,
      }}
    >
      <div
        style={{
          background: 'rgba(30, 30, 40, 0.85)',
          borderRadius: 32,
          boxShadow: '0 4px 32px rgba(0,0,0,0.25)',
          padding: '8vw 4vw',
          maxWidth: 700,
          width: '96vw',
          margin: '8vw 0',
          position: 'relative',
          zIndex: 1,
        }}
      >
        <header style={{ textAlign: 'center', marginBottom: 40 }}>
          <h1 style={{ fontSize: 40, fontWeight: 700, margin: 0, color: '#ff6ec4', letterSpacing: 1 }}>Aryan Sharma</h1>
          <p style={{ fontSize: 18, color: '#b2bec3', marginTop: 8, minHeight: 28 }}>
            {typedText}
            <span style={{ color: '#ff6ec4', fontWeight: 700 }}>|</span>
          </p>
        </header>
        <section style={{ marginBottom: 36 }}>
          <h2 style={{ color: '#7873f5', fontSize: 28, marginBottom: 8 }}>About Me</h2>
          <p style={{ fontSize: 17, color: '#dfe6e9' }}>
            Hi, I'm Aryan Sharma, currently pursuing a Bachelor's Degree. I'm passionate about coding, learning, and developing new things. This site showcases my work and lets you chat with my AI assistant to learn more about me.
          </p>
        </section>
        <section style={{ marginBottom: 36 }}>
          <h2 style={{ color: '#7873f5', fontSize: 28, marginBottom: 8 }}>Projects</h2>
          <ul style={{ fontSize: 17, color: '#dfe6e9', paddingLeft: 20 }}>
            <li>Chatbot Website</li>
            <li>Portfolio Builder</li>
            <li>AI Experiments</li>
          </ul>
        </section>
        <section>
          <h2 style={{ color: '#7873f5', fontSize: 28, marginBottom: 8 }}>Contact</h2>
          <p style={{ fontSize: 17, color: '#dfe6e9' }}>Email: aryanxsharma26@gmail.com</p>
        </section>
      </div>
      <Chatbot />
    </div>
  );
}

export default App;
