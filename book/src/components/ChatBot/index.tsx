import React, { useState, useRef, useEffect, useCallback } from "react";
import styles from "./ChatBot.module.css";

const API_URL =
  process.env.NODE_ENV === "production"
    ? "https://YOUR_BACKEND_URL/api/v1"
    : "http://localhost:8000/api/v1";

interface Source {
  text: string;
  source: string;
  chapter: string;
  title: string;
  score: number;
}

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  selectedText?: string;
  isStreaming?: boolean;
}

interface ChatBotProps {
  initialSelectedText?: string;
  onClose?: () => void;
  embedded?: boolean;
}

export default function ChatBot({
  initialSelectedText,
  onClose,
  embedded = false,
}: ChatBotProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [selectedText, setSelectedText] = useState(initialSelectedText || "");
  const [showSources, setShowSources] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (initialSelectedText) {
      setSelectedText(initialSelectedText);
    }
  }, [initialSelectedText]);

  // Add welcome message
  useEffect(() => {
    setMessages([
      {
        id: "welcome",
        role: "assistant",
        content: initialSelectedText
          ? `I can see you selected some text from the book. What would you like to know about it?`
          : `Hello! I'm the Physical AI Book assistant. I can answer questions about the book's content on topics like robotics, machine learning, computer vision, sim-to-real transfer, embodied AI, humanoid robots, and more.\n\nYou can also **select any text** in the book and ask me about it specifically!`,
      },
    ]);
  }, []);

  const sendMessage = useCallback(async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      selectedText: selectedText || undefined,
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentInput = input;
    const currentSelectedText = selectedText;
    setInput("");
    setSelectedText("");
    setIsLoading(true);

    // Add streaming assistant message placeholder
    const streamingId = (Date.now() + 1).toString();
    setMessages((prev) => [
      ...prev,
      {
        id: streamingId,
        role: "assistant",
        content: "",
        isStreaming: true,
      },
    ]);

    try {
      const response = await fetch(`${API_URL}/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          conversation_id: conversationId,
          message: currentInput,
          selected_text: currentSelectedText || null,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const reader = response.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let sources: Source[] = [];
      let fullContent = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));

              if (data.type === "conversation_id") {
                setConversationId(data.data);
              } else if (data.type === "sources") {
                sources = data.data;
              } else if (data.type === "text") {
                fullContent += data.data;
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === streamingId
                      ? { ...m, content: fullContent, isStreaming: true }
                      : m
                  )
                );
              } else if (data.type === "done") {
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === streamingId
                      ? { ...m, content: fullContent, sources, isStreaming: false }
                      : m
                  )
                );
              }
            } catch {
              // Skip malformed SSE data
            }
          }
        }
      }
    } catch (error) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === streamingId
            ? {
                ...m,
                content:
                  "Sorry, I couldn't connect to the backend. Please make sure the API server is running.",
                isStreaming: false,
              }
            : m
        )
      );
    } finally {
      setIsLoading(false);
    }
  }, [input, isLoading, conversationId, selectedText]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: "welcome-new",
        role: "assistant",
        content:
          "Chat cleared! Ask me anything about Physical AI.",
      },
    ]);
    setConversationId(null);
    setSelectedText("");
  };

  return (
    <div className={`${styles.chatbot} ${embedded ? styles.embedded : ""}`}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.headerTitle}>
          <span className={styles.botIcon}>🤖</span>
          <div>
            <div className={styles.titleText}>Physical AI Assistant</div>
            <div className={styles.subtitleText}>RAG-powered book chatbot</div>
          </div>
        </div>
        <div className={styles.headerActions}>
          <button
            className={styles.clearBtn}
            onClick={clearChat}
            title="Clear chat"
          >
            🗑️
          </button>
          {onClose && (
            <button className={styles.closeBtn} onClick={onClose} title="Close">
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Selected text banner */}
      {selectedText && (
        <div className={styles.selectedTextBanner}>
          <span className={styles.selectedIcon}>📌</span>
          <span className={styles.selectedPreview}>
            {selectedText.length > 80
              ? selectedText.slice(0, 80) + "..."
              : selectedText}
          </span>
          <button
            className={styles.clearSelected}
            onClick={() => setSelectedText("")}
          >
            ✕
          </button>
        </div>
      )}

      {/* Messages */}
      <div className={styles.messages}>
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`${styles.message} ${
              msg.role === "user" ? styles.userMessage : styles.assistantMessage
            }`}
          >
            {msg.role === "assistant" && (
              <div className={styles.avatar}>🤖</div>
            )}
            <div className={styles.messageContent}>
              {msg.selectedText && (
                <div className={styles.selectedTextQuote}>
                  <em>Re: "{msg.selectedText.slice(0, 60)}..."</em>
                </div>
              )}
              <div
                className={`${styles.bubble} ${
                  msg.isStreaming ? styles.streaming : ""
                }`}
              >
                <MarkdownContent content={msg.content} />
                {msg.isStreaming && <span className={styles.cursor}>▊</span>}
              </div>
              {msg.sources && msg.sources.length > 0 && (
                <div className={styles.sourcesSection}>
                  <button
                    className={styles.sourcesToggle}
                    onClick={() =>
                      setShowSources(showSources === msg.id ? null : msg.id)
                    }
                  >
                    📚 {msg.sources.length} source
                    {msg.sources.length !== 1 ? "s" : ""}
                    {showSources === msg.id ? " ▲" : " ▼"}
                  </button>
                  {showSources === msg.id && (
                    <div className={styles.sourcesList}>
                      {msg.sources.map((src, i) => (
                        <div key={i} className={styles.sourceItem}>
                          <div className={styles.sourceHeader}>
                            <span className={styles.sourceTitle}>
                              {src.title}
                            </span>
                            <span className={styles.sourceScore}>
                              {(src.score * 100).toFixed(0)}% match
                            </span>
                          </div>
                          <div className={styles.sourceChapter}>
                            {src.chapter}
                          </div>
                          <div className={styles.sourceText}>{src.text}</div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
            {msg.role === "user" && <div className={styles.avatar}>👤</div>}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className={styles.inputArea}>
        <textarea
          ref={inputRef}
          className={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about Physical AI... (Enter to send, Shift+Enter for newline)"
          rows={2}
          disabled={isLoading}
        />
        <button
          className={styles.sendBtn}
          onClick={sendMessage}
          disabled={isLoading || !input.trim()}
        >
          {isLoading ? (
            <span className={styles.loadingDots}>...</span>
          ) : (
            "Send →"
          )}
        </button>
      </div>
    </div>
  );
}

// Simple markdown renderer (avoid heavy libraries)
function MarkdownContent({ content }: { content: string }) {
  if (!content) return null;

  // Convert basic markdown to HTML-safe JSX
  const lines = content.split("\n");
  const elements: React.ReactNode[] = [];

  let inCodeBlock = false;
  let codeLines: string[] = [];
  let codeLang = "";

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    if (line.startsWith("```")) {
      if (!inCodeBlock) {
        inCodeBlock = true;
        codeLang = line.slice(3).trim();
        codeLines = [];
      } else {
        elements.push(
          <pre key={i} className={styles.codeBlock}>
            <code>{codeLines.join("\n")}</code>
          </pre>
        );
        inCodeBlock = false;
        codeLines = [];
      }
      continue;
    }

    if (inCodeBlock) {
      codeLines.push(line);
      continue;
    }

    if (line.startsWith("### ")) {
      elements.push(<h3 key={i}>{line.slice(4)}</h3>);
    } else if (line.startsWith("## ")) {
      elements.push(<h2 key={i}>{line.slice(3)}</h2>);
    } else if (line.startsWith("# ")) {
      elements.push(<h1 key={i}>{line.slice(2)}</h1>);
    } else if (line.startsWith("- ") || line.startsWith("* ")) {
      elements.push(
        <li key={i} className={styles.listItem}>
          {formatInline(line.slice(2))}
        </li>
      );
    } else if (line.trim() === "") {
      elements.push(<br key={i} />);
    } else {
      elements.push(<p key={i}>{formatInline(line)}</p>);
    }
  }

  return <div className={styles.markdownContent}>{elements}</div>;
}

function formatInline(text: string): React.ReactNode {
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={i}>{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith("`") && part.endsWith("`")) {
      return <code key={i} className={styles.inlineCode}>{part.slice(1, -1)}</code>;
    }
    return part;
  });
}
