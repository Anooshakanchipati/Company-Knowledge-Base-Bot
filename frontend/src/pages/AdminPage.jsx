import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  checkAdminAccess,
  deleteDocument,
  getDocuments,
  uploadDocuments,
} from "../services/adminApi";

import "./AdminPage.css";

function AdminPage() {
  const [documents, setDocuments] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);

  async function loadDocuments() {
    

    try {
      await checkAdminAccess();
      const data = await getDocuments();

      // Supports either an array or { documents: [...] }
      setDocuments(
        Array.isArray(data) ? data : data.documents || []
      );
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setIsLoading(false);
    }
  }

 useEffect(() => {
  let isActive = true;

  Promise.all([
    checkAdminAccess(),
    getDocuments(),
  ])
    .then(([, data]) => {
      if (!isActive) return;

      setDocuments(
        Array.isArray(data) ? data : data.documents || []
      );
    })
    .catch((requestError) => {
      if (isActive) {
        setError(requestError.message);
      }
    })
    .finally(() => {
      if (isActive) {
        setIsLoading(false);
      }
    });

  return () => {
    isActive = false;
  };
}, []);

  function handleFileChange(event) {
    setSelectedFiles(Array.from(event.target.files));
    setMessage("");
    setError("");
  }

  async function handleUpload(event) {
    event.preventDefault();

    if (selectedFiles.length === 0) {
      setError("Please select at least one document.");
      return;
    }

    setIsUploading(true);
    setError("");
    setMessage("");

    try {
      await uploadDocuments(selectedFiles);

      setMessage("Documents uploaded successfully.");
      setSelectedFiles([]);

      const fileInput = document.getElementById(
        "document-files"
      );

      if (fileInput) {
        fileInput.value = "";
      }

      await loadDocuments();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setIsUploading(false);
    }
  }

  async function handleDelete(documentId, filename) {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${filename}"?`
    );

    if (!confirmed) {
      return;
    }

    setError("");
    setMessage("");

    try {
      await deleteDocument(documentId);
      setMessage("Document deleted successfully.");
      await loadDocuments();
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  return (
    <main className="admin-page">
      <header className="admin-header">
        <div>
          <h1>Admin Dashboard</h1>
          <p>Manage knowledge-base documents</p>
        </div>

        <Link to="/chat" className="back-to-chat">
          Back to Chat
        </Link>
      </header>

      <section className="admin-content">
        <div className="upload-card">
          <h2>Upload Documents</h2>

          <p>
            Select one or multiple documents to add to the
            knowledge base.
          </p>

          <form onSubmit={handleUpload}>
            <input
              id="document-files"
              type="file"
              multiple
              accept=".pdf,.txt,.doc,.docx,.csv"
              onChange={handleFileChange}
            />

            {selectedFiles.length > 0 && (
              <div className="selected-files">
                <strong>Selected files:</strong>

                <ul>
                  {selectedFiles.map((file) => (
                    <li key={`${file.name}-${file.size}`}>
                      {file.name}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <button type="submit" disabled={isUploading}>
              {isUploading
                ? "Uploading..."
                : "Upload Documents"}
            </button>
          </form>
        </div>

        {message && (
          <div className="admin-success">{message}</div>
        )}

        {error && (
          <div className="admin-error">{error}</div>
        )}

        <div className="documents-card">
          <div className="documents-heading">
            <div>
              <h2>Uploaded Documents</h2>
              <p>{documents.length} document(s)</p>
            </div>

            <button
              className="refresh-button"
              onClick={loadDocuments}
              type="button"
            >
              Refresh
            </button>
          </div>

          {isLoading ? (
            <p className="empty-message">
              Loading documents...
            </p>
          ) : documents.length === 0 ? (
            <p className="empty-message">
              No documents have been uploaded yet.
            </p>
          ) : (
            <div className="document-list">
              {documents.map((document) => {
                const documentId =
                  document.id || document.document_id;

                const filename =
                  document.filename ||
                  document.name ||
                  "Document";

                return (
                  <div
                    className="document-item"
                    key={documentId}
                  >
                    <div className="document-icon">DOC</div>

                    <div className="document-details">
                      <h3>{filename}</h3>

                      <p>
                        {document.status ||
                          "Available in knowledge base"}
                      </p>
                    </div>

                    <button
                      className="delete-button"
                      type="button"
                      onClick={() =>
                        handleDelete(
                          documentId,
                          filename
                        )
                      }
                    >
                      Delete
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </section>
    </main>
  );
}

export default AdminPage;