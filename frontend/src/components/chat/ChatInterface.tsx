"use client";

import React, { useState, useRef, useEffect } from "react";
import { useSession } from "next-auth/react";
import styles from "./ChatInterface.module.css";

interface Message {
  id: number;
  role: "user" | "assistant" | "tool";
  content: string;
  created_at: string;
}

interface ChatInterfaceProps {
  conversationId?: number;
  onClose?: () => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  conversationId,
  onClose,
}) => {
  const { data: session } = useSession();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input;
    setInput("");
    setLoading(true);

    try {
      const response = await fetch("/api/chat/send", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session?.user?.id}`,
        },
        body: JSON.stringify({
          content: userMessage,
          conversation_id: conversationId,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setMessages((prev) => [
          ...prev,
          { id: data.message_id, role: "user", content: userMessage, created_at: new Date().toISOString() },
          { id: data.message_id + 1, role: "assistant", content: data.content, created_at: new Date().toISOString() },
        ]);
      }
    } catch (error) {
      console.error("Error sending message:", error);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) {
    return (
      <button
        className={styles.chatButton}
        onClick={() => setIsOpen(true)}
        title="Open chat"
      >
        💬
      </button>
    );
  }

  return (
    <div className={styles.chatContainer}>
      <div className={styles.chatHeader}>
        <h3>Chat Assistant</h3>
        <button
          className={styles.closeButton}
          onClick={() => {
            setIsOpen(false);
            onClose?.();
          }}
        >
          ✕
        </button>
      </div>

      <div className={styles.messagesContainer}>
        {messages.map((msg) => (
          <div key={msg.id} className={`${styles.message} ${styles[msg.role]}`}>
            <p>{msg.content}</p>
          </div>
        ))}
        {loading && (
          <div className={`${styles.message} ${styles.assistant}`}>
            <p className={styles.typing}>Thinking...</p>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className={styles.inputContainer}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === "Enter") {
              handleSendMessage();
            }
          }}
          placeholder="Type a message..."
          disabled={loading}
          className={styles.input}
        />
        <button
          onClick={handleSendMessage}
          disabled={loading || !input.trim()}
          className={styles.sendButton}
        >
          Send
        </button>
      </div>
    </div>
  );
};
