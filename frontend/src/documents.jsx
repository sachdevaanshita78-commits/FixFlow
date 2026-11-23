
import { useCallback, useEffect, useRef, useState } from "react";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000/api/v1";

const ALLOWED_EXTENSIONS = [".pdf", ".docx", ".txt",".md"];
const MAX_FILE_SIZE = 10 * 1024 * 1024;

async function apiRequest(path, options = {}) {
  const token = localStorage.getItem("access_token");

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      ...(options.body instanceof FormData
        ? {}
        : options.body
          ? { "Content-Type": "application/json" }
          : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  const text = await response.text();
  let data = {};

  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    data = { detail: text || "Unexpected server response" };
  }

  if (!response.ok) {
    throw new Error(
      data.detail || data.message || `Request failed (${response.status})`
    );
  }

  return data;
}

function formatDate(value) {
  if (!value) return "—";

  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? value
    : date.toLocaleString();
}

function getDocumentName(document) {
  return (
    document.filename ||
    document.original_filename ||
    document.name ||
    "Untitled document"
  );
}

function formatSize(bytes) {
  if (typeof bytes !== "number") return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

export default function Documents() {
  const fileInputRef = useRef(null);

  const [documents, setDocuments] = useState([]);
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState({ completed: 0, total: 0 });
  const [deletingId, setDeletingId] = useState(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const loadDocuments = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const result = await apiRequest("/documents");
      setDocuments(
        Array.isArray(result)
          ? result
          : Array.isArray(result.documents)
            ? result.documents
            : []
      );
    } catch (err) {
      setError(err.message || "Could not load documents.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  function handleFileSelection(event) {
    const selectedFiles = Array.from(event.target.files || []);
    const validFiles = [];
    const errors = [];

    for (const file of selectedFiles) {
      const filename = file.name.toLowerCase();
      const supported = ALLOWED_EXTENSIONS.some((extension) =>
        filename.endsWith(extension)
      );

      if (!supported) {
        errors.push(`${file.name}: only PDF, DOCX, and TXT files are supported.`);
        continue;
      }

      if (file.size === 0) {
        errors.push(`${file.name}: the file is empty.`);
        continue;
      }

      if (file.size > MAX_FILE_SIZE) {
        errors.push(`${file.name}: the maximum file size is 10 MB.`);
        continue;
      }

      validFiles.push(file);
    }

    setFiles((previous) => {
      const combined = [...previous];

      for (const file of validFiles) {
        const alreadySelected = combined.some(
          (existing) =>
            existing.name === file.name &&
            existing.size === file.size &&
            existing.lastModified === file.lastModified
        );

        if (!alreadySelected) {
          combined.push(file);
        }
      }

      return combined;
    });

    setError(errors.join("\n"));
    setNotice("");

    // Allows the user to select the same file again later.
    event.target.value = "";
  }

  function removeFile(indexToRemove) {
    setFiles((previous) =>
      previous.filter((_, index) => index !== indexToRemove)
    );
  }

  async function handleUpload(event) {
    event.preventDefault();

    if (files.length === 0) {
      setError("Choose at least one document to upload.");
      return;
    }

    const filesToUpload = [...files];
    const successfulFiles = [];
    const failedFiles = [];

    setUploading(true);
    setError("");
    setNotice("");
    setProgress({ completed: 0, total: filesToUpload.length });

    for (let index = 0; index < filesToUpload.length; index += 1) {
      const file = filesToUpload[index];

      try {
        const formData = new FormData();

        // The current backend accepts one file per request.
        formData.append("file", file);

        await apiRequest("/documents", {
          method: "POST",
          body: formData,
        });

        successfulFiles.push(file);
      } catch (err) {
        failedFiles.push({
          name: file.name,
          message: err.message || "Upload failed.",
        });
      }

      setProgress({
        completed: index + 1,
        total: filesToUpload.length,
      });
    }

    // Remove only successful uploads; failed files remain selected for retry.
    setFiles((previous) =>
      previous.filter(
        (file) =>
          !successfulFiles.some(
            (uploaded) =>
              uploaded.name === file.name &&
              uploaded.size === file.size &&
              uploaded.lastModified === file.lastModified
          )
      )
    );

    if (successfulFiles.length > 0) {
      setNotice(
        `Uploaded ${successfulFiles.length} of ${filesToUpload.length} document(s) successfully.`
      );
    }

    if (failedFiles.length > 0) {
      setError(
        failedFiles
          .map((file) => `${file.name}: ${file.message}`)
          .join("\n")
      );
    }

    await loadDocuments();

    setUploading(false);
    setProgress({ completed: 0, total: 0 });
  }

  async function handleDelete(document) {
    const id = document.id ?? document.document_id;

    if (!id) {
      setError("This document has no ID, so it cannot be deleted.");
      return;
    }

    if (!window.confirm(`Delete "${getDocumentName(document)}"?`)) {
      return;
    }

    setDeletingId(id);
    setError("");
    setNotice("");

    try {
      await apiRequest(`/documents/${encodeURIComponent(id)}`, {
        method: "DELETE",
      });

      setDocuments((current) =>
        current.filter(
          (item) =>
            String(item.id ?? item.document_id) !== String(id)
        )
      );

      setNotice("Document deleted successfully.");
    } catch (err) {
      setError(err.message || "Could not delete the document.");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="fx-documents-page">
      <section className="fx-panel">
        <div className="fx-panel-heading">
          <div>
            <span className="fx-eyebrow">COMPANY KNOWLEDGE BASE</span>
            <h2>Upload company policies</h2>
            <p>
              Select multiple organization policies and reference documents
              at once. These files will be used for the chatbot knowledge
              base in a later step.
            </p>
          </div>
        </div>

        {error && (
          <div className="fx-alert fx-alert-error" role="alert">
            {error.split("\n").map((line, index) => (
              <div key={`${index}-${line}`}>{line}</div>
            ))}
          </div>
        )}

        {notice && (
          <div className="fx-alert fx-alert-success" role="status">
            {notice}
          </div>
        )}

        <form className="fx-form" onSubmit={handleUpload}>
          <label>
            Select policy documents
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.txt,.md,application/pdf,text/plain,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              multiple
              onChange={handleFileSelection}
              disabled={uploading}
            />
          </label>

          <p className="fx-muted">
            Select several files together using Ctrl + click, or select a
            range using Shift + click. You can also open the picker again
            to add more files.
          </p>

          {files.length > 0 && (
            <>
              <p className="fx-muted">
                {files.length} document(s) selected.
              </p>

              <div className="fx-table-wrap">
                <table className="fx-table">
                  <thead>
                    <tr>
                      <th>File name</th>
                      <th>Size</th>
                      <th>Action</th>
                    </tr>
                  </thead>

                  <tbody>
                    {files.map((file, index) => (
                      <tr
                        key={`${file.name}-${file.size}-${file.lastModified}`}
                      >
                        <td>{file.name}</td>
                        <td>{formatSize(file.size)}</td>
                        <td>
                          <button
                            type="button"
                            className="fx-button fx-button-small fx-button-light"
                            onClick={() => removeFile(index)}
                            disabled={uploading}
                          >
                            Remove
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}

          <p className="fx-muted">
            Supported formats: PDF, DOCX, TXT. Maximum 10 MB per file.
          </p>

          {uploading && (
            <p className="fx-muted" role="status">
              Uploading document {progress.completed} of {progress.total}…
            </p>
          )}

          <div className="fx-actions">
            <button
              type="button"
              className="fx-button fx-button-light"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
            >
              Add more documents
            </button>

            <button
              type="submit"
              className="fx-button fx-button-primary"
              disabled={uploading || files.length === 0}
            >
              {uploading
                ? "Uploading…"
                : `Upload ${files.length} document(s)`}
            </button>
          </div>
        </form>
      </section>

      <section className="fx-panel">
        <div className="fx-panel-heading">
          <div>
            <h2>Company documents</h2>
            <p>
              Documents uploaded to your company's knowledge base.
            </p>
          </div>

          <div className="fx-actions">
            <span className="fx-count-pill">
              {documents.length} documents
            </span>

            <button
              type="button"
              className="fx-button fx-button-light"
              onClick={loadDocuments}
              disabled={loading || uploading}
            >
              {loading ? "Loading…" : "Refresh"}
            </button>
          </div>
        </div>

        {loading ? (
          <div className="fx-loading">
            <span className="fx-spinner" />
            Loading documents…
          </div>
        ) : documents.length === 0 ? (
          <div className="fx-empty-state">
            No documents uploaded yet. Upload your first company policy above.
          </div>
        ) : (
          <div className="fx-table-wrap">
            <table className="fx-table">
              <thead>
                <tr>
                  <th>Document</th>
                  <th>Uploaded</th>
                  <th>Size</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>
                {documents.map((document) => {
                  const id = document.id ?? document.document_id;

                  return (
                    <tr key={id}>
                      <td>{getDocumentName(document)}</td>
                      <td>
                        {formatDate(
                          document.created_at || document.uploaded_at
                        )}
                      </td>
                      <td>{formatSize(document.file_size)}</td>
                      <td>
                        <button
                          type="button"
                          className="fx-button fx-button-small fx-button-light"
                          disabled={deletingId === id || uploading}
                          onClick={() => handleDelete(document)}
                        >
                          {deletingId === id ? "Deleting…" : "Delete"}
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
