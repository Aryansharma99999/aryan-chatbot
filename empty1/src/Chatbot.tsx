import React, { useState } from 'react';

const faqs: { q: string; a: string; keywords: string[] }[] = [
  {
    q: "Where were you born?",
    a: "Aryan was born in Punjab — land of lassi and bhangra. 🥳",
    keywords: ["born", "birth", "punjab"]
  },
  {
    q: "Where do you live now?",
    a: "In the beautiful mountains of Himachal Pradesh 🌄.",
    keywords: ["live", "location", "himachal", "mountain"]
  },
  {
    q: "What do you love the most?",
    a: "Coffee ☕. Without it, Aryan is basically on airplane mode.",
    keywords: ["love", "most", "favorite", "coffee"]
  },
  {
    q: "How many girlfriends do you have?",
    a: "None 😅. But coffee keeps him warm, so no complaints.",
    keywords: ["girlfriend", "relationship", "love life"]
  },
  {
    q: "Are you a writer?",
    a: "Yup! Aryan writes stories, thoughts, and maybe a few secret rants too. ✍️",
    keywords: ["writer", "write", "stories", "author"]
  },
  {
    q: "What’s your relationship status?",
    a: "Married to coffee. ☕❤️",
    keywords: ["relationship", "status", "married"]
  },
  {
    q: "What’s your hobby?",
    a: "Writing, exploring ideas, and overthinking like a pro.",
    keywords: ["hobby", "hobbies", "interest"]
  },
  {
    q: "Who are you?",
    a: "I’m Aryan’s chatbot, his virtual twin with more sarcasm. 😎",
    keywords: ["who", "you", "chatbot", "virtual"]
  },
  {
    q: "What’s your dream?",
    a: "To write something legendary and maybe own a coffee shop in the mountains one day. 🌲☕",
    keywords: ["dream", "goal", "ambition"]
  },
  {
    q: "Do you like traveling?",
    a: "Yes! Especially when the trip ends with coffee and mountain views.",
    keywords: ["travel", "trip", "vacation"]
  },
  {
    q: "What’s your favorite drink?",
    a: "Need you even ask? Coffee. Always coffee.",
    keywords: ["drink", "favorite", "coffee"]
  },
  {
    q: "What kind of person is Aryan?",
    a: "Chill, creative, funny — and slightly addicted to caffeine.",
    keywords: ["person", "character", "personality"]
  },
  {
    q: "Do you party a lot?",
    a: "Not really. His idea of a party = coffee + notebook + peace ✌️.",
    keywords: ["party", "fun", "celebrate"]
  },
  {
    q: "Any secret talent?",
    a: "Aryan can turn everyday life into stories. And also make people laugh randomly.",
    keywords: ["talent", "secret", "skill"]
  },
  {
    q: "What motivates you?",
    a: "Coffee first… then dreams, goals, and the hope of fewer Monday mornings. 😂",
    keywords: ["motivate", "motivation", "inspire"]
  }
];

function getResponse(input: string): string {
  const text = input.toLowerCase();
  for (const faq of faqs) {
    if (faq.keywords.some(k => text.includes(k))) {
      return faq.a;
    }
  }
  if (text.includes('name')) return "My name is Aryan Sharma.";
  if (text.includes('degree') || text.includes('study')) return "I'm currently pursuing a Bachelor's Degree.";
  if (text.includes('email') || text.includes('contact')) return "You can contact me at aryanxsharma26@gmail.com.";
  if (text.includes('passion') || text.includes('interest')) return "I'm passionate about coding, learning, and developing new things.";
  if (text.includes('hi') || text.includes('hello')) return "Hi! Ask me anything about Aryan.";
  return "I'm Aryan's AI assistant. Ask me about Aryan's background, interests, or contact info!";
}

const Chatbot: React.FC = () => {
  const [messages, setMessages] = useState([
    { from: 'bot', text: 'Hi! Ask me questions about Aryan.' }
  ]);
  const [input, setInput] = useState('');
  const [showFAQ, setShowFAQ] = useState(false);

  const sendMessage = () => {
    if (!input.trim()) return;
    const userMsg = { from: 'user', text: input };
    const botMsg = { from: 'bot', text: getResponse(input) };
    setMessages([...messages, userMsg, botMsg]);
    setInput('');
  };

  return (
    <div
      style={{
        position: 'fixed',
        right: '4vw',
        bottom: '4vw',
        width: '90vw',
        maxWidth: 340,
        background: 'linear-gradient(135deg, #232526 0%, #414345 100%)',
        border: '1px solid #222',
        borderRadius: 16,
        boxShadow: '0 4px 24px rgba(0,0,0,0.25)',
        padding: '4vw',
        zIndex: 1000,
        color: '#f5f6fa',
        fontFamily: 'Inter, Arial, sans-serif',
      }}
    >
      <div
        style={{ marginBottom: 10, fontWeight: 'bold', color: '#00c3ff', fontSize: 18, cursor: 'pointer' }}
        onClick={() => setShowFAQ((prev) => !prev)}
        title="Click to see FAQ"
      >
        Aryan's AI Chatbot
        <span style={{ marginLeft: 8, fontSize: 14, color: '#fff', background: '#00c3ff', borderRadius: 6, padding: '2px 8px' }}>FAQ</span>
      </div>
      {showFAQ && (
        <div style={{
          background: '#232526',
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
          padding: 12,
          marginBottom: 12,
          maxHeight: 180,
          overflowY: 'auto',
          color: '#f5f6fa',
        }}>
          <div style={{ fontWeight: 600, marginBottom: 8, color: '#ff6ec4' }}>Frequently Asked Questions</div>
          <ul style={{ paddingLeft: 18, margin: 0 }}>
            {faqs.map((faq, idx) => (
              <li key={idx} style={{ marginBottom: 8, fontSize: 15 }}>
                <span style={{ color: '#00c3ff' }}>Q:</span> {faq.q}
              </li>
            ))}
          </ul>
        </div>
      )}
      <div style={{ maxHeight: 180, overflowY: 'auto', marginBottom: 10 }}>
        {messages.map((msg, idx) => (
          <div key={idx} style={{ textAlign: msg.from === 'bot' ? 'left' : 'right', margin: '6px 0' }}>
            <span style={{ background: msg.from === 'bot' ? '#353b48' : '#00c3ff', color: msg.from === 'bot' ? '#f5f6fa' : '#232526', padding: '6px 12px', borderRadius: 8, display: 'inline-block' }}>{msg.text}</span>
          </div>
        ))}
      </div>
      <div style={{ display: 'flex' }}>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && sendMessage()}
          placeholder="Type your question..."
          style={{ flex: 1, padding: '8px 12px', borderRadius: 8, border: '1px solid #222', marginRight: 6, background: '#232526', color: '#f5f6fa' }}
        />
        <button onClick={sendMessage} style={{ padding: '8px 16px', borderRadius: 8, background: '#00c3ff', color: '#232526', border: 'none', fontWeight: 600 }}>
          Send
        </button>
      </div>
    </div>
  );
};

export default Chatbot;
