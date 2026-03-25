import { useState } from "react";
import axios from "axios";

function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);

  const sendQuery = async () => {
    if (!question) return;

    const userMsg = { role: "user", text: question };
    setMessages(prev => [...prev, userMsg]);

    try {
      const res = await axios.post("http://127.0.0.1:8000/api/query", {
        question: question
      });

      const botMsg = {
        role: "bot",
        text: res.data.answer,
        sql: res.data.sql,
        result: res.data.result
      };

      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        { role: "bot", text: "Error fetching response" }
      ]);
    }

    setQuestion("");
  };

  return (
    <div style={{ padding: 20, fontFamily: "Arial" }}>
      <h2>💬 Data Chat System</h2>

      <div style={{ marginBottom: 20 }}>
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask something..."
          style={{ width: "70%", padding: 10 }}
        />
        <button onClick={sendQuery} style={{ padding: 10, marginLeft: 10 }}>
          Send
        </button>
      </div>

      <div>
        {messages.map((msg, index) => (
          <div key={index} style={{ marginBottom: 20 }}>
            <b>{msg.role === "user" ? "You" : "Bot"}:</b>
            <div>{msg.text}</div>

            {msg.sql && (
              <pre style={{ background: "#eee", padding: 10 }}>
                SQL: {msg.sql}
              </pre>
            )}

            {msg.result && (
              <pre style={{ background: "#f5f5f5", padding: 10 }}>
                {JSON.stringify(msg.result, null, 2)}
              </pre>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;