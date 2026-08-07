import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import {
  askQuestion,
  deleteConversation,
  getConversation,
  getConversations,
} from "../services/chatApi";
import {
  getCurrentUser,
  logoutUser,
} from "../services/authApi";
import "./ChatPage.css";

function ChatPage() {
  const navigate = useNavigate();

  const [question, setQuestion] = useState("");
  const [conversationId, setConversationId] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [error, setError] = useState("");
const [isAdmin, setIsAdmin] = useState(false);
  useEffect(() => {
  async function loadChatPage() {
    await loadConversations();

    try {
      const user = await getCurrentUser();

      const hasAdminAccess =
        user?.role?.toLowerCase() === "admin" ||
        user?.is_admin === true;

      setIsAdmin(hasAdminAccess);
    } catch {
      setIsAdmin(false);
    }
  }

  loadChatPage();
}, []);

  async function loadConversations() {
    try {
      setHistoryLoading(true);
      const data = await getConversations();
      setConversations(Array.isArray(data) ? data : []);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setHistoryLoading(false);
    }
  }

  async function openConversation(selectedId) {
    if (isLoading) return;

    try {
      setError("");
      const data = await getConversation(selectedId);

      setConversationId(data.id);
      setMessages(data.messages || []);
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  async function handleDelete(event, selectedId) {
    event.stopPropagation();

    const shouldDelete = window.confirm(
      "Do you want to delete this conversation?"
    );

    if (!shouldDelete) return;

    try {
      await deleteConversation(selectedId);

      if (conversationId === selectedId) {
        startNewConversation();
      }

      await loadConversations();
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();

    const cleanedQuestion = question.trim();

    if (!cleanedQuestion || isLoading) return;

    setMessages((currentMessages) => [
      ...currentMessages,
      {
        role: "user",
        content: cleanedQuestion,
      },
    ]);

    setQuestion("");
    setError("");
    setIsLoading(true);

    try {
      const data = await askQuestion(
        cleanedQuestion,
        conversationId
      );

      setConversationId(data.conversation_id);

      setMessages((currentMessages) => [
        ...currentMessages,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources,
          modelProvider: data.model_provider,
        },
      ]);

      await loadConversations();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setIsLoading(false);
    }
  }

  function startNewConversation() {
    setConversationId(null);
    setMessages([]);
    setQuestion("");
    setError("");
  }

  function handleLogout() {
    logoutUser();
    navigate("/login", { replace: true });
  }

  return (
    <div className="chat-layout">
      <aside className="chat-sidebar">
        <div className="sidebar-brand">
          <div className="brand-icon">K</div>

          <div>
            <h2>Knowledge Base</h2>
            <p>AI Assistant</p>
          </div>
        </div>

        <button
          type="button"
          className="sidebar-new-chat"
          onClick={startNewConversation}
        >
          + New Chat
        </button>

        <div className="history-heading">
          <span>Chat History</span>

          <button
            type="button"
            onClick={loadConversations}
            title="Refresh history"
          >
            ↻
          </button>
        </div>

        <div className="conversation-list">
          {historyLoading && (
            <p className="history-status">Loading history...</p>
          )}

          {!historyLoading && conversations.length === 0 && (
            <p className="history-status">
              No conversations yet.
            </p>
          )}

          {conversations.map((conversation) => (
            <button
              type="button"
              key={conversation.id}
              className={`conversation-item ${
                conversationId === conversation.id
                  ? "active"
                  : ""
              }`}
              onClick={() =>
                openConversation(conversation.id)
              }
            >
              <span className="conversation-details">
                <strong>{conversation.title}</strong>

                <small>
                  {conversation.created_at
                    ? new Date(
                        conversation.created_at
                      ).toLocaleDateString()
                    : ""}
                </small>
              </span>

              <span
                role="button"
                tabIndex={0}
                className="delete-chat-button"
                title="Delete conversation"
                onClick={(event) =>
                  handleDelete(event, conversation.id)
                }
                onKeyDown={(event) => {
                  if (
                    event.key === "Enter" ||
                    event.key === " "
                  ) {
                    handleDelete(event, conversation.id);
                  }
                }}
              >
                ×
              </span>
            </button>
          ))}
        </div>

        <nav className="sidebar-navigation">
          <button
            type="button"
            onClick={() => navigate("/dashboard")}
          >
            Dashboard
          </button>

        {isAdmin && (
  <button
    type="button"
    onClick={() => navigate("/admin")}
  >
    Admin
  </button>
)}

          <button
            type="button"
            className="sidebar-logout"
            onClick={handleLogout}
          >
            Logout
          </button>
        </nav>
      </aside>

      <section className="chat-page">
        <header className="chat-header">
          <div>
            <h1>Company Knowledge Assistant</h1>
            
          </div>

          {/* <button
            type="button"
            className="new-chat-button"
            onClick={startNewConversation}
          >
            New Chat
          </button> */}
        </header>

        <main className="message-list">
          {messages.length === 0 && (
            <section className="welcome-card">
              <div className="welcome-icon">✨</div>
              <h2>How can I help you?</h2>

              <p>
                Ask about company policies, employee benefits,
                procedures, or IT guidelines.
              </p>
            </section>
          )}

          {messages.map((message, index) => (
            <article
              key={message.id || `${message.role}-${index}`}
              className={`message ${message.role}`}
            >
              <div className="message-label">
                {message.role === "user"
                  ? "You"
                  : "Assistant"}
              </div>

              <div className="message-content">
  <ReactMarkdown>
    {message.content}
  </ReactMarkdown>
</div>

              {message.modelProvider && (
                <div className="model-provider">
                  Answered using {message.modelProvider}
                </div>
              )}

              {message.sources?.length > 0 && (
                <div className="sources">
                  <strong>Sources</strong>

                  {message.sources.map((source) => (
                    <span
                      key={`${source.document_id}-${source.chunk_number}`}
                      className="source-chip"
                    >
                      {source.document_name} — Chunk{" "}
                      {source.chunk_number}
                    </span>
                  ))}
                </div>
              )}
            </article>
          ))}

          {isLoading && (
            <article className="message assistant">
              <div className="message-label">Assistant</div>

              <div className="message-content">
                Searching company documents...
              </div>
            </article>
          )}

          {error && (
            <div className="chat-error">{error}</div>
          )}
        </main>

        <form className="chat-form" onSubmit={handleSubmit}>
          <textarea
            value={question}
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            onKeyDown={(event) => {
              if (
                event.key === "Enter" &&
                !event.shiftKey
              ) {
                event.preventDefault();
                handleSubmit(event);
              }
            }}
            placeholder="Ask a question about company information..."
            rows="2"
            disabled={isLoading}
          />

          <button
            type="submit"
            disabled={!question.trim() || isLoading}
          >
            {isLoading ? "Thinking..." : "Send"}
          </button>
        </form>
      </section>
    </div>
  );
}

export default ChatPage;