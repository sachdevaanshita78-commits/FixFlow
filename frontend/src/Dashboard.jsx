import { useCallback, useEffect, useState } from "react";
import "./dashboard.css";
import Documents from "./documents";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL ||
  "/api/v1";

const ROLE_DETAILS = {
  platform_admin: {
    title: "Platform Admin",
    subtitle: "Manage organizations and monitor the FixFlow platform.",
  },
  admin: {
    title: "Company Admin",
    subtitle: "Manage your company's tickets, team, and policy documents.",
  },
  agent: {
    title: "Employee Dashboard",
    subtitle: "Track tickets and access your company workspace.",
  },
};

const EMPTY_METRICS = {
  total_companies: 0,
  total_users: 0,
  total_tickets: 0,
  open_tickets: 0,
  in_progress_tickets: 0,
  resolved_tickets: 0,
};

function readStoredUser() {
  try {
    const raw = localStorage.getItem("user");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

async function apiRequest(path, options = {}) {
  const token = localStorage.getItem("access_token");

  const headers = {
    ...(options.body && !(options.body instanceof FormData)
      ? { "Content-Type": "application/json" }
      : {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  const text = await response.text();
  let data = {};

  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    data = { detail: text || "Unexpected server response." };
  }

  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("token_type");
      localStorage.removeItem("user");
    }

    throw new Error(
      data.detail || data.message || `Request failed (${response.status}).`
    );
  }

  return data;
}

function formatDate(value) {
  if (!value) return "—";

  const date = new Date(value);

  return Number.isNaN(date.getTime())
    ? String(value)
    : date.toLocaleDateString();
}

function statusClass(status) {
  return String(status || "unknown")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-");
}

function getTicketId(ticket) {
  return ticket?.id ?? ticket?.ticket_id;
}

function getTicketDescription(ticket) {
  const fields = [
    "description",
    "body",
    "content",
    "details",
    "message",
    "issue_description",
  ];

  for (const field of fields) {
    const value = ticket?.[field];

    if (typeof value === "string" && value.trim()) {
      return value.trim();
    }
  }

  return "";
}

function getRequestId(request) {
  return request?.id ?? request?.request_id;
}

function getCompanyId(company) {
  return company?.id ?? company?.tenant_id;
}

function getList(data, keys = []) {
  if (Array.isArray(data)) return data;

  for (const key of keys) {
    if (Array.isArray(data?.[key])) return data[key];
  }

  return [];
}

function StatCard({ label, value, description }) {
  return (
    <article className="fx-stat-card">
      <span className="fx-stat-label">{label}</span>
      <strong className="fx-stat-value">{value}</strong>
      {description && (
        <span className="fx-stat-description">{description}</span>
      )}
    </article>
  );
}

function EmptyState({ children }) {
  return <div className="fx-empty-state">{children}</div>;
}

function TicketTable({
  tickets,
  onSelect,
  selectedId,
  canDelete = false,
  onDelete,
  deletingId,
}) {
  if (!tickets.length) {
    return <EmptyState>No tickets found for this workspace.</EmptyState>;
  }

  return (
    <div className="fx-table-wrap">
      <table className="fx-table">
        <thead>
          <tr>
            <th>Ticket</th>
            <th>Title</th>
            <th>Status</th>
            <th>Priority</th>
            <th>Created</th>
            <th>Details</th>
            {canDelete && <th>Actions</th>}
          </tr>
        </thead>

        <tbody>
          {tickets.map((ticket) => {
            const id = getTicketId(ticket);
            const isDeleting = String(deletingId) === String(id);
            const isSelected = String(selectedId) === String(id);

            return (
              <tr key={id}>
                <td>#{String(id ?? "—").slice(0, 8)}</td>
                <td>{ticket.title || ticket.subject || "Untitled ticket"}</td>
                <td>
                  <span
                    className={`fx-status fx-status-${statusClass(
                      ticket.status
                    )}`}
                  >
                    {ticket.status || "Unknown"}
                  </span>
                </td>
                <td>{ticket.priority || "Normal"}</td>
                <td>{formatDate(ticket.created_at)}</td>
                <td>
                  <button
                    className="fx-button fx-button-small fx-button-light"
                    type="button"
                    onClick={() => onSelect(ticket)}
                  >
                    {isSelected ? "Selected" : "View"}
                  </button>
                </td>

                {canDelete && (
                  <td>
                    <button
                      className="fx-button fx-button-small fx-button-danger"
                      type="button"
                      disabled={isDeleting}
                      onClick={() => onDelete(ticket)}
                    >
                      {isDeleting ? "Deleting…" : "Delete"}
                    </button>
                  </td>
                )}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function TicketDetails({
  ticket,
  onClose,
  canDelete,
  onDelete,
  deletingId,
  aiResult,
  aiLoading,
  aiError,
  aiQuestion,
  setAiQuestion,
  onGenerateAnswer,
}) {
  if (!ticket) {
    return (
      <section className="fx-panel">
        <EmptyState>
          Select a ticket from the table to view its description and generate
          an AI-assisted response.
        </EmptyState>
      </section>
    );
  }

  const id = getTicketId(ticket);
  const description = getTicketDescription(ticket);
  const isDeleting = String(deletingId) === String(id);

  return (
    <section className="fx-panel fx-ticket-details">
      <div className="fx-panel-heading">
        <div>
          <span className="fx-eyebrow">TICKET DETAILS</span>
          <h3>{ticket.title || ticket.subject || "Ticket"}</h3>
        </div>

        <div className="fx-actions">
          {canDelete && (
            <button
              type="button"
              className="fx-button fx-button-danger"
              disabled={isDeleting}
              onClick={() => onDelete(ticket)}
            >
              {isDeleting ? "Deleting…" : "Delete ticket"}
            </button>
          )}

          <button
            type="button"
            className="fx-button fx-button-light"
            onClick={onClose}
          >
            Close
          </button>
        </div>
      </div>

      <div className="fx-detail-grid">
        <div>
          <span className="fx-detail-label">Ticket ID</span>
          <p>{id ?? "—"}</p>
        </div>
        <div>
          <span className="fx-detail-label">Status</span>
          <p>{ticket.status || "Unknown"}</p>
        </div>
        <div>
          <span className="fx-detail-label">Priority</span>
          <p>{ticket.priority || "Normal"}</p>
        </div>
        <div>
          <span className="fx-detail-label">Created</span>
          <p>{formatDate(ticket.created_at)}</p>
        </div>
      </div>

      <div className="fx-description-section">
        <span className="fx-detail-label">Description</span>
        <p className="fx-ticket-description">
          {description || "No description was returned by the ticket API."}
        </p>
      </div>

      {ticket.status === "auto_answered" && ticket.reply && (
        <div className="fx-ai-result">
          <h4>Automatic customer reply</h4>
          <div className="fx-ai-answer">{ticket.reply}</div>
        </div>
      )}

      <div className="fx-ai-panel">
        <div className="fx-panel-heading">
          <div>
            <span className="fx-eyebrow">FIXFLOW AI</span>
            <h3>AI-assisted ticket response</h3>
            <p>
              Generate a suggested answer using relevant company knowledge
              retrieved by RAG.
            </p>
          </div>
        </div>

        <form
          className="fx-form"
          onSubmit={(event) => {
            event.preventDefault();
            onGenerateAnswer(ticket);
          }}
        >
          <label>
            Question for the AI
            <textarea
              value={aiQuestion}
              onChange={(event) => setAiQuestion(event.target.value)}
              placeholder="What troubleshooting steps should we recommend?"
              rows={3}
              required
            />
          </label>

          <button
            className="fx-button fx-button-primary"
            type="submit"
            disabled={aiLoading || !aiQuestion.trim()}
          >
            {aiLoading ? "Generating response…" : "Generate AI response"}
          </button>
        </form>

        {aiError && (
          <div className="fx-alert fx-alert-error" role="alert">
            {aiError}
          </div>
        )}

        {aiResult && (
          <div className="fx-ai-result">
            <div className="fx-ai-result-heading">
              <h4>Generated response</h4>
              <span
                className={`fx-ai-status ${
                  aiResult.insufficient_evidence
                    ? "fx-ai-status-warning"
                    : "fx-ai-status-success"
                }`}
              >
                {aiResult.insufficient_evidence
                  ? "Insufficient evidence"
                  : "Evidence found"}
              </span>
            </div>

            <div className="fx-ai-answer">
              {aiResult.answer || "The AI endpoint returned no answer."}
            </div>

            {aiResult.citations?.length > 0 && (
              <div className="fx-ai-citations">
                <strong>Sources</strong>
                <ul>
                  {aiResult.citations.map((citation, index) => (
                    <li key={index}>
                      {typeof citation === "string"
                        ? citation
                        : citation.source ||
                          citation.filename ||
                          citation.title ||
                          JSON.stringify(citation)}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <p className="fx-muted">
              This is an AI-generated suggestion. Review it before using it
              in a customer response.
            </p>
          </div>
        )}
      </div>
    </section>
  );
}

function InviteEmployeeForm({ onInvited }) {
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    setError("");

    try {
      const result = await apiRequest("/invitations", {
        method: "POST",
        body: JSON.stringify({
          email: email.trim(),
          full_name: fullName.trim(),
        }),
      });

      setMessage(result.message || "Invitation sent successfully.");
      setEmail("");
      setFullName("");
      await onInvited?.();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="fx-form" onSubmit={handleSubmit}>
      {message && (
        <div className="fx-alert fx-alert-success">{message}</div>
      )}
      {error && <div className="fx-alert fx-alert-error">{error}</div>}

      <label>
        Employee name
        <input
          type="text"
          value={fullName}
          onChange={(event) => setFullName(event.target.value)}
          placeholder="Employee name"
          minLength={2}
          required
        />
      </label>

      <label>
        Employee email
        <input
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          placeholder="employee@company.com"
          required
        />
      </label>

      <button
        className="fx-button fx-button-primary"
        type="submit"
        disabled={busy}
      >
        {busy ? "Sending…" : "Invite employee"}
      </button>

      <p className="fx-muted">
        Invitations are sent through your configured backend email service.
      </p>
    </form>
  );
}

function CompanyList({ companies }) {
  if (!companies.length) {
    return <EmptyState>No companies were returned by the API.</EmptyState>;
  }

  return (
    <div className="fx-company-list">
      {companies.map((company) => {
        const id = getCompanyId(company);
        const ownerEmail =
          company.owner_email ||
          company.admin_email ||
          company.owner?.email ||
          company.admin?.email ||
          company.email;

        return (
          <div className="fx-company-row" key={id}>
            <span className="fx-company-avatar">
              {(company.name || "C").slice(0, 1).toUpperCase()}
            </span>
            <span className="fx-company-info">
              <strong>{company.name || "Unnamed company"}</strong>
              <small>{ownerEmail || "Owner/admin email unavailable"}</small>
            </span>
          </div>
        );
      })}
    </div>
  );
}

function OrganizationRequestsPanel({
  requests,
  loading,
  error,
  actionId,
  onRefresh,
  onAction,
}) {
  return (
    <section className="fx-panel">
      <div className="fx-panel-heading">
        <div>
          <h2>Organization registration requests</h2>
          <p>Review company registrations and decide whether to approve them.</p>
        </div>

        <button
          type="button"
          className="fx-button fx-button-light"
          onClick={onRefresh}
          disabled={loading}
        >
          {loading ? "Refreshing…" : "Refresh"}
        </button>
      </div>

      {error && (
        <div className="fx-alert fx-alert-error" role="alert">
          {error}
        </div>
      )}

      {loading ? (
        <EmptyState>Loading organization requests…</EmptyState>
      ) : requests.length === 0 ? (
        <EmptyState>No organization registration requests found.</EmptyState>
      ) : (
        <div className="fx-table-wrap">
          <table className="fx-table">
            <thead>
              <tr>
                <th>Company</th>
                <th>Admin name</th>
                <th>Email</th>
                <th>Status</th>
                <th>Submitted</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              {requests.map((request) => {
                const id = getRequestId(request);
                const pending =
                  String(request.status || "").toLowerCase() === "pending";
                const busy = String(actionId) === String(id);

                return (
                  <tr key={id}>
                    <td>{request.company_name || "—"}</td>
                    <td>{request.admin_name || "—"}</td>
                    <td>{request.email || "—"}</td>
                    <td>
                      <span
                        className={`fx-status fx-status-${statusClass(
                          request.status
                        )}`}
                      >
                        {request.status || "pending"}
                      </span>
                    </td>
                    <td>{formatDate(request.created_at)}</td>
                    <td>
                      {pending ? (
                        <div className="fx-actions">
                          <button
                            type="button"
                            className="fx-button fx-button-small fx-button-primary"
                            disabled={busy}
                            onClick={() => onAction(request, "approve")}
                          >
                            {busy ? "Processing…" : "Approve"}
                          </button>
                          <button
                            type="button"
                            className="fx-button fx-button-small fx-button-danger"
                            disabled={busy}
                            onClick={() => onAction(request, "reject")}
                          >
                            Reject
                          </button>
                        </div>
                      ) : (
                        <span className="fx-muted">Already reviewed</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function CompaniesManagementPanel({
  companies,
  deletingId,
  onDelete,
}) {
  return (
    <section className="fx-panel">
      <div className="fx-panel-heading">
        <div>
          <h2>Registered companies</h2>
          <p>
            View registered company workspaces and permanently delete a
            company when necessary.
          </p>
        </div>

        <span className="fx-count-pill">
          {companies.length} companies
        </span>
      </div>

      {!companies.length ? (
        <EmptyState>No companies found.</EmptyState>
      ) : (
        <div className="fx-table-wrap">
          <table className="fx-table">
            <thead>
              <tr>
                <th>Company</th>
                <th>Admin email</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              {companies.map((company) => {
                const id = getCompanyId(company);
                const busy = String(deletingId) === String(id);
                const email =
                  company.owner_email ||
                  company.admin_email ||
                  company.owner?.email ||
                  company.admin?.email ||
                  company.email;

                return (
                  <tr key={id}>
                    <td>{company.name || "Unnamed company"}</td>
                    <td>{email || "Not available"}</td>
                    <td>{formatDate(company.created_at)}</td>
                    <td>
                      <button
                        type="button"
                        className="fx-button fx-button-small fx-button-danger"
                        disabled={busy || id == null}
                        onClick={() => onDelete(company)}
                      >
                        {busy ? "Deleting…" : "Delete company"}
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
  );
}

export default function Dashboard({ onNavigate }) {
  const [user, setUser] = useState(() => readStoredUser());

  const [tickets, setTickets] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [invitations, setInvitations] = useState([]);

  const [organizationRequests, setOrganizationRequests] = useState([]);
  const [requestsLoading, setRequestsLoading] = useState(false);
  const [requestsError, setRequestsError] = useState("");
  const [requestActionId, setRequestActionId] = useState(null);

  const [teamLoading, setTeamLoading] = useState(false);
  const [teamError, setTeamError] = useState("");

  const [metrics, setMetrics] = useState(EMPTY_METRICS);
  const [metricsLoading, setMetricsLoading] = useState(false);
  const [metricsError, setMetricsError] = useState("");

  const [selectedTicket, setSelectedTicket] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [deletingId, setDeletingId] = useState(null);
  const [deletingCompanyId, setDeletingCompanyId] = useState(null);
  const [deletingInvitationId, setDeletingInvitationId] = useState(null);

  const [aiQuestion, setAiQuestion] = useState("");
  const [aiResult, setAiResult] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState("");

  const role = user?.role;
  const roleDetails = ROLE_DETAILS[role];
  const canDelete = role === "admin";

  const loadPlatformMetrics = useCallback(async () => {
    setMetricsLoading(true);
    setMetricsError("");

    try {
      const data = await apiRequest("/platform/metrics");

      setMetrics({
        total_companies: Number(data.total_companies ?? 0),
        total_users: Number(data.total_users ?? 0),
        total_tickets: Number(data.total_tickets ?? 0),
        open_tickets: Number(data.open_tickets ?? 0),
        in_progress_tickets: Number(data.in_progress_tickets ?? 0),
        resolved_tickets: Number(data.resolved_tickets ?? 0),
      });
    } catch (err) {
      setMetricsError(err.message || "Unable to load platform metrics.");
    } finally {
      setMetricsLoading(false);
    }
  }, []);

  const loadOrganizationRequests = useCallback(async () => {
    if (user?.role !== "platform_admin") return;

    setRequestsLoading(true);
    setRequestsError("");

    try {
      const data = await apiRequest("/platform/organization-requests");

      setOrganizationRequests(
        getList(data, ["requests", "items", "organization_requests"])
      );
    } catch (err) {
      setRequestsError(
        err.message || "Unable to load organization registration requests."
      );
    } finally {
      setRequestsLoading(false);
    }
  }, [user?.role]);

  const loadDashboard = useCallback(async () => {
    setLoading(true);
    setError("");
    setNotice("");

    try {
      const token = localStorage.getItem("access_token");

      if (!token) {
        throw new Error("You are not logged in. Please sign in again.");
      }

      const currentUser = await apiRequest("/auth/me");

      setUser(currentUser);
      localStorage.setItem("user", JSON.stringify(currentUser));

      if (!ROLE_DETAILS[currentUser.role]) {
        throw new Error(`Unsupported user role: ${currentUser.role}`);
      }

      if (currentUser.role === "platform_admin") {
        const companyData = await apiRequest("/tenants");
        setCompanies(getList(companyData, ["companies", "tenants"]));
        setTickets([]);
        setSelectedTicket(null);

        await Promise.all([
          loadPlatformMetrics(),
          loadOrganizationRequests(),
        ]);
      } else {
        const ticketData = await apiRequest("/tickets");
        setTickets(getList(ticketData, ["tickets"]));
        setCompanies([]);
      }
    } catch (err) {
      setError(err.message || "Unable to load dashboard.");

      if (!localStorage.getItem("access_token")) {
        onNavigate?.("/login");
      }
    } finally {
      setLoading(false);
    }
  }, [onNavigate, loadPlatformMetrics, loadOrganizationRequests]);

  const loadTeamData = useCallback(async () => {
    if (user?.role !== "admin") return;

    setTeamLoading(true);
    setTeamError("");

    try {
      const [employeeData, invitationData] = await Promise.all([
        apiRequest("/tenants/users"),
        apiRequest("/invitations"),
      ]);

      setEmployees(getList(employeeData, ["users", "employees"]));
      setInvitations(getList(invitationData, ["invitations", "items"]));
    } catch (err) {
      setTeamError(err.message || "Unable to load team information.");
    } finally {
      setTeamLoading(false);
    }
  }, [user?.role]);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  useEffect(() => {
    if (
      !loading &&
      role === "admin" &&
      ["employees", "invitations"].includes(activeTab)
    ) {
      loadTeamData();
    }
  }, [loading, role, activeTab, loadTeamData]);

  async function handleOrganizationRequest(request, action) {
    if (role !== "platform_admin") {
      setRequestsError("Only platform administrators can review requests.");
      return;
    }

    const id = getRequestId(request);

    if (!id) {
      setRequestsError("This organization request has no ID.");
      return;
    }

    const companyName = request.company_name || "this organization";

    const confirmed = window.confirm(
      `${action === "approve" ? "Approve" : "Reject"} the registration request for "${companyName}"?`
    );

    if (!confirmed) return;

    setRequestActionId(id);
    setRequestsError("");
    setError("");
    setNotice("");

    try {
      await apiRequest(
        `/platform/organization-requests/${encodeURIComponent(id)}/${action}`,
        { method: "POST" }
      );

      setNotice(
        action === "approve"
          ? `${companyName} has been approved.`
          : `${companyName}'s registration request has been rejected.`
      );

      await loadOrganizationRequests();

      if (action === "approve") {
        const companyData = await apiRequest("/tenants");
        setCompanies(getList(companyData, ["companies", "tenants"]));
        await loadPlatformMetrics();
      }
    } catch (err) {
      setRequestsError(
        err.message || `Unable to ${action} this organization request.`
      );
    } finally {
      setRequestActionId(null);
    }
  }

  async function handleDeleteCompany(company) {
    if (role !== "platform_admin") {
      setError("Only platform administrators can delete companies.");
      return;
    }

    const id = getCompanyId(company);

    if (!id) {
      setError("Cannot delete this company because its ID is missing.");
      return;
    }

    const companyName = company.name || "this company";

    const confirmed = window.confirm(
      `Permanently delete "${companyName}" and its associated records? This action cannot be undone.`
    );

    if (!confirmed) return;

    setDeletingCompanyId(id);
    setError("");
    setNotice("");

    try {
      const result = await apiRequest(
        `/tenants/${encodeURIComponent(id)}`,
        { method: "DELETE" }
      );

      setCompanies((current) =>
        current.filter(
          (item) => String(getCompanyId(item)) !== String(id)
        )
      );

      setNotice(result.message || `${companyName} was deleted successfully.`);

      await loadPlatformMetrics();

      if (activeTab === "overview") {
        const companyData = await apiRequest("/tenants");
        setCompanies(getList(companyData, ["companies", "tenants"]));
      }
    } catch (err) {
      setError(err.message || "Unable to delete this company.");
    } finally {
      setDeletingCompanyId(null);
    }
  }

  async function handleDeleteTicket(ticket) {
    if (role !== "admin") {
      setError("Only company admins can delete tickets.");
      return;
    }

    const id = getTicketId(ticket);

    if (id == null) {
      setError("Cannot delete this ticket because its ID is missing.");
      return;
    }

    const confirmed = window.confirm(
      `Delete ticket "${ticket.title || ticket.subject || id}"? This action cannot be undone.`
    );

    if (!confirmed) return;

    setDeletingId(id);
    setError("");
    setNotice("");

    try {
      await apiRequest(`/tickets/${encodeURIComponent(id)}`, {
        method: "DELETE",
      });

      setTickets((current) =>
        current.filter((item) => String(getTicketId(item)) !== String(id))
      );

      setSelectedTicket((current) =>
        current && String(getTicketId(current)) === String(id)
          ? null
          : current
      );

      setAiResult(null);
      setNotice("Ticket deleted successfully.");
    } catch (err) {
      setError(err.message || "Unable to delete ticket.");
    } finally {
      setDeletingId(null);
    }
  }

  async function handleDeleteInvitation(invitation) {
    if (role !== "admin") {
      setError("Only company admins can delete invitations.");
      return;
    }

    const id = invitation?.id;

    if (!id) {
      setError("Cannot delete this invitation because its ID is missing.");
      return;
    }

    const email = invitation.email || "this invitation";
    const confirmed = window.confirm(
      `Delete the invitation for ${email}? This action cannot be undone.`
    );

    if (!confirmed) return;

    setDeletingInvitationId(id);
    setError("");
    setNotice("");

    try {
      const result = await apiRequest(
        `/invitations/${encodeURIComponent(id)}`,
        { method: "DELETE" }
      );

      setInvitations((current) =>
        current.filter((item) => String(item.id) !== String(id))
      );
      setNotice(result.message || "Invitation deleted successfully.");
    } catch (err) {
      setError(err.message || "Unable to delete this invitation.");
    } finally {
      setDeletingInvitationId(null);
    }
  }

  async function handleGenerateAnswer(ticket) {
    if (!ticket) return;

    const id = getTicketId(ticket);

    if (id == null) {
      setAiError("This ticket has no ID.");
      return;
    }

    if (!aiQuestion.trim()) {
      setAiError("Enter a question for the AI.");
      return;
    }

    setAiLoading(true);
    setAiError("");
    setAiResult(null);

    try {
      const result = await apiRequest(
        `/tickets/${encodeURIComponent(id)}/ai-answer`,
        {
          method: "POST",
          body: JSON.stringify({
            question: aiQuestion.trim(),
          }),
        }
      );

      setAiResult({
        answer: result.answer ?? result.response ?? "",
        insufficient_evidence: Boolean(result.insufficient_evidence),
        citations: Array.isArray(result.citations) ? result.citations : [],
      });
    } catch (err) {
      setAiError(err.message || "Unable to generate an AI response.");
    } finally {
      setAiLoading(false);
    }
  }

  function selectTicket(ticket) {
    setSelectedTicket(ticket);
    setActiveTab("tickets");
    setAiResult(null);
    setAiError("");
    setAiQuestion(
      `How should we resolve this issue: ${
        ticket.title || ticket.subject || "the customer's issue"
      }?`
    );
  }

  function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("token_type");
    localStorage.removeItem("user");
    onNavigate?.("/login");
  }

  if (loading) {
    return (
      <main className="fx-dashboard">
        <div className="fx-loading">
          <span className="fx-spinner" />
          Loading your FixFlow workspace…
        </div>
      </main>
    );
  }

  if (error && !roleDetails) {
    return (
      <main className="fx-dashboard">
        <div className="fx-dashboard-message">
          <h2>Unable to open your dashboard</h2>
          <p>{error}</p>
          <div className="fx-actions">
            <button
              className="fx-button fx-button-primary"
              onClick={loadDashboard}
            >
              Try again
            </button>
            <button className="fx-button fx-button-light" onClick={logout}>
              Sign in again
            </button>
          </div>
        </div>
      </main>
    );
  }

  if (!roleDetails) return null;

  const openCount = tickets.filter(
    (ticket) =>
      !["closed", "resolved"].includes(
        String(ticket.status || "").toLowerCase()
      )
  ).length;

  const urgentCount = tickets.filter(
    (ticket) => String(ticket.priority || "").toLowerCase() === "urgent"
  ).length;

  return (
    <main className="fx-dashboard">
      <header className="fx-topbar">
        <button
          className="fx-brand"
          type="button"
          onClick={() => onNavigate?.("/")}
          aria-label="Go to FixFlow homepage"
        >
          <span className="fx-brand-mark">F</span>
          <span>FixFlow</span>
        </button>

        <div className="fx-topbar-right">
          <div className="fx-user-summary">
            <span className="fx-user-avatar">
              {(user?.full_name || user?.email || "U")
                .slice(0, 1)
                .toUpperCase()}
            </span>
            <span>
              <strong>{user?.full_name || user?.email || "User"}</strong>
              <small>{roleDetails.title}</small>
            </span>
          </div>

          <button
            type="button"
            className="fx-button fx-button-light"
            onClick={logout}
          >
            Log out
          </button>
        </div>
      </header>

      <div className="fx-dashboard-layout">
        <aside className="fx-sidebar">
          <span className="fx-sidebar-label">WORKSPACE</span>

          <button
            type="button"
            className={`fx-nav-item ${activeTab === "overview" ? "active" : ""}`}
            onClick={() => setActiveTab("overview")}
          >
            <span>▦</span> Overview
          </button>

          {role === "platform_admin" && (
            <>
              <button
                type="button"
                className={`fx-nav-item ${activeTab === "companies" ? "active" : ""}`}
                onClick={() => setActiveTab("companies")}
              >
                <span>▤</span> Companies
              </button>

              <button
                type="button"
                className={`fx-nav-item ${
                  activeTab === "organization-requests" ? "active" : ""
                }`}
                onClick={() => setActiveTab("organization-requests")}
              >
                <span>✉</span> Organization Requests
              </button>
            </>
          )}

          {role !== "platform_admin" && (
            <button
              type="button"
              className={`fx-nav-item ${activeTab === "tickets" ? "active" : ""}`}
              onClick={() => setActiveTab("tickets")}
            >
              <span>▣</span> Tickets
            </button>
          )}

          {role === "admin" && (
            <>
              <button
                type="button"
                className={`fx-nav-item ${activeTab === "employees" ? "active" : ""}`}
                onClick={() => setActiveTab("employees")}
              >
                <span>♙</span> Employees
              </button>

              <button
                type="button"
                className={`fx-nav-item ${activeTab === "documents" ? "active" : ""}`}
                onClick={() => setActiveTab("documents")}
              >
                <span>▤</span> Documents
              </button>

              <button
                type="button"
                className={`fx-nav-item ${activeTab === "invite" ? "active" : ""}`}
                onClick={() => setActiveTab("invite")}
              >
                <span>＋</span> Invite employees
              </button>

              <button
                type="button"
                className={`fx-nav-item ${activeTab === "invitations" ? "active" : ""}`}
                onClick={() => setActiveTab("invitations")}
              >
                <span>✉</span> Invitations
              </button>
            </>
          )}

          {role === "agent" && (
            <button
              type="button"
              className={`fx-nav-item ${activeTab === "company" ? "active" : ""}`}
              onClick={() => setActiveTab("company")}
            >
              <span>⌂</span> Company details
            </button>
          )}

          <div className="fx-sidebar-bottom">
            <div className="fx-help-card">
              <strong>Need help?</strong>
              <p>Keep your support workflow organized with FixFlow.</p>
            </div>
          </div>
        </aside>

        <section className="fx-main-content">
          <div className="fx-page-heading">
            <div>
              <span className="fx-eyebrow">FIXFLOW WORKSPACE</span>
              <h1>
                {activeTab === "overview"
                  ? `Welcome${user?.full_name ? `, ${user.full_name.split(" ")[0]}` : ""}`
                  : activeTab === "companies"
                    ? "Companies"
                    : activeTab === "organization-requests"
                      ? "Organization Requests"
                      : activeTab === "tickets"
                        ? "Tickets"
                        : activeTab === "employees"
                          ? "Company employees"
                          : activeTab === "documents"
                            ? "Company documents"
                            : activeTab === "invite"
                              ? "Invite employees"
                              : activeTab === "invitations"
                                ? "Invitation statuses"
                                : "Company details"}
              </h1>

              <p>
                {activeTab === "organization-requests"
                  ? "Review and manage company registration requests."
                  : activeTab === "companies"
                    ? "Manage registered company workspaces."
                    : activeTab === "documents"
                      ? "Upload and manage your company's policy documents."
                      : activeTab === "employees"
                        ? "Review team members belonging to your company."
                        : activeTab === "invitations"
                          ? "Review pending, accepted, and expired invitations."
                          : roleDetails.subtitle}
              </p>
            </div>

            <button
              type="button"
              className="fx-button fx-button-light"
              onClick={() => {
                loadDashboard();
                if (role === "admin") loadTeamData();
              }}
            >
              ↻ Refresh
            </button>
          </div>

          {error && <div className="fx-alert fx-alert-error">{error}</div>}
          {notice && <div className="fx-alert fx-alert-info">{notice}</div>}

          {activeTab === "documents" && role === "admin" && <Documents />}

          {activeTab === "organization-requests" &&
            role === "platform_admin" && (
              <OrganizationRequestsPanel
                requests={organizationRequests}
                loading={requestsLoading}
                error={requestsError}
                actionId={requestActionId}
                onRefresh={loadOrganizationRequests}
                onAction={handleOrganizationRequest}
              />
            )}

          {activeTab === "overview" && (
            <>
              <div className="fx-stat-grid">
                {role === "platform_admin" ? (
                  <>
                    <StatCard
                      label="Companies"
                      value={
                        metricsLoading ? "Loading…" : metrics.total_companies
                      }
                      description="Registered company workspaces"
                    />
                    <StatCard
                      label="Total users"
                      value={metricsLoading ? "Loading…" : metrics.total_users}
                      description="Company admins and employees"
                    />
                    <StatCard
                      label="Total tickets"
                      value={
                        metricsLoading ? "Loading…" : metrics.total_tickets
                      }
                      description="Across all company workspaces"
                    />
                  </>
                ) : (
                  <>
                    <StatCard
                      label="Total tickets"
                      value={tickets.length}
                      description="Tickets in your company workspace"
                    />
                    <StatCard
                      label="Open tickets"
                      value={openCount}
                      description="Tickets not closed or resolved"
                    />
                    <StatCard
                      label="Urgent tickets"
                      value={urgentCount}
                      description="Tickets with urgent priority"
                    />
                  </>
                )}
              </div>

              {role === "platform_admin" && (
                <>
                  <section className="fx-panel">
                    <div className="fx-panel-heading">
                      <div>
                        <h2>Ticket status overview</h2>
                        <p>Aggregate ticket counts across the platform.</p>
                      </div>
                      <button
                        className="fx-button fx-button-light"
                        onClick={loadPlatformMetrics}
                        disabled={metricsLoading}
                      >
                        Refresh metrics
                      </button>
                    </div>

                    {metricsError && (
                      <div className="fx-alert fx-alert-error">
                        {metricsError}
                      </div>
                    )}

                    <div className="fx-stat-grid">
                      <StatCard label="Open" value={metrics.open_tickets} />
                      <StatCard
                        label="In progress"
                        value={metrics.in_progress_tickets}
                      />
                      <StatCard
                        label="Resolved"
                        value={metrics.resolved_tickets}
                      />
                    </div>
                  </section>

                  <section className="fx-panel">
                    <div className="fx-panel-heading">
                      <div>
                        <h2>Company workspaces</h2>
                        <p>Company names and owner/admin contact emails.</p>
                      </div>
                      <button
                        className="fx-button fx-button-light"
                        onClick={() => setActiveTab("companies")}
                      >
                        View all
                      </button>
                    </div>
                    <CompanyList companies={companies.slice(0, 5)} />
                  </section>

                  <section className="fx-panel">
                    <div className="fx-panel-heading">
                      <div>
                        <h2>Organization requests</h2>
                        <p>Review companies waiting for approval.</p>
                      </div>
                      <button
                        className="fx-button fx-button-light"
                        onClick={() => setActiveTab("organization-requests")}
                      >
                        Review requests
                      </button>
                    </div>

                    {requestsLoading ? (
                      <EmptyState>Loading requests…</EmptyState>
                    ) : (
                      <p>
                        {organizationRequests.filter(
                          (request) =>
                            String(request.status || "").toLowerCase() ===
                            "pending"
                        ).length}{" "}
                        pending registration request(s).
                      </p>
                    )}

                    {requestsError && (
                      <div className="fx-alert fx-alert-error">
                        {requestsError}
                      </div>
                    )}
                  </section>
                </>
              )}

              {role !== "platform_admin" && (
                <section className="fx-panel">
                  <div className="fx-panel-heading">
                    <div>
                      <h2>Recent tickets</h2>
                      <p>The latest tickets in your workspace.</p>
                    </div>
                    <button
                      className="fx-button fx-button-light"
                      onClick={() => setActiveTab("tickets")}
                    >
                      View all
                    </button>
                  </div>

                  <TicketTable
                    tickets={tickets.slice(0, 5)}
                    selectedId={getTicketId(selectedTicket)}
                    onSelect={selectTicket}
                    canDelete={canDelete}
                    onDelete={handleDeleteTicket}
                    deletingId={deletingId}
                  />
                </section>
              )}

              {role === "admin" && (
                <section className="fx-panel">
                  <div className="fx-panel-heading">
                    <div>
                      <h2>Quick actions</h2>
                      <p>Manage your support team, documents, and tickets.</p>
                    </div>
                  </div>

                  <div className="fx-quick-actions">
                    <button
                      className="fx-action-card"
                      onClick={() => setActiveTab("invite")}
                    >
                      <span className="fx-action-icon">＋</span>
                      <strong>Invite an employee</strong>
                      <small>Add a team member by email</small>
                    </button>

                    <button
                      className="fx-action-card"
                      onClick={() => setActiveTab("employees")}
                    >
                      <span className="fx-action-icon">♙</span>
                      <strong>View employees</strong>
                      <small>Review your company team</small>
                    </button>

                    <button
                      className="fx-action-card"
                      onClick={() => setActiveTab("tickets")}
                    >
                      <span className="fx-action-icon">▣</span>
                      <strong>Manage tickets</strong>
                      <small>Review and delete company tickets</small>
                    </button>

                    <button
                      className="fx-action-card"
                      onClick={() => setActiveTab("documents")}
                    >
                      <span className="fx-action-icon">▤</span>
                      <strong>Manage documents</strong>
                      <small>Upload company policies</small>
                    </button>
                  </div>
                </section>
              )}
            </>
          )}

          {activeTab === "companies" && role === "platform_admin" && (
            <CompaniesManagementPanel
              companies={companies}
              deletingId={deletingCompanyId}
              onDelete={handleDeleteCompany}
            />
          )}

          {activeTab === "tickets" && role !== "platform_admin" && (
            <>
              <section className="fx-panel">
                <div className="fx-panel-heading">
                  <div>
                    <h2>All tickets</h2>
                    <p>
                      {canDelete
                        ? "Review, track, and delete tickets for your company."
                        : "View tickets in your company workspace."}
                    </p>
                  </div>
                  <span className="fx-count-pill">
                    {tickets.length} tickets
                  </span>
                </div>

                <TicketTable
                  tickets={tickets}
                  selectedId={getTicketId(selectedTicket)}
                  onSelect={selectTicket}
                  canDelete={canDelete}
                  onDelete={handleDeleteTicket}
                  deletingId={deletingId}
                />
              </section>

              <TicketDetails
                ticket={selectedTicket}
                onClose={() => {
                  setSelectedTicket(null);
                  setAiResult(null);
                  setAiError("");
                }}
                canDelete={canDelete}
                onDelete={handleDeleteTicket}
                deletingId={deletingId}
                aiResult={aiResult}
                aiLoading={aiLoading}
                aiError={aiError}
                aiQuestion={aiQuestion}
                setAiQuestion={setAiQuestion}
                onGenerateAnswer={handleGenerateAnswer}
              />
            </>
          )}

          {activeTab === "employees" && role === "admin" && (
            <section className="fx-panel">
              <div className="fx-panel-heading">
                <div>
                  <h2>Company employees</h2>
                  <p>Members who belong to your company workspace.</p>
                </div>
                <span className="fx-count-pill">
                  {employees.length} employees
                </span>
              </div>

              {teamError && (
                <div className="fx-alert fx-alert-error" role="alert">
                  {teamError}
                </div>
              )}

              {teamLoading ? (
                <EmptyState>Loading employees...</EmptyState>
              ) : employees.length === 0 && !teamError ? (
                <EmptyState>
                  No employees found.
                  <div style={{ marginTop: "1rem" }}>
                    <button
                      className="fx-button fx-button-primary"
                      onClick={() => setActiveTab("invite")}
                    >
                      Invite an employee
                    </button>
                  </div>
                </EmptyState>
              ) : (
                <div className="fx-table-wrap">
                  <table className="fx-table">
                    <thead>
                      <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Role</th>
                        <th>Joined</th>
                      </tr>
                    </thead>
                    <tbody>
                      {employees.map((employee) => (
                        <tr key={employee.id}>
                          <td>{employee.full_name || "—"}</td>
                          <td>{employee.email}</td>
                          <td>
                            <span className="fx-status">
                              {employee.role || "agent"}
                            </span>
                          </td>
                          <td>{formatDate(employee.created_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          )}

          {activeTab === "invite" && role === "admin" && (
            <section className="fx-panel fx-form-panel">
              <div className="fx-panel-heading">
                <div>
                  <h2>Invite a team member</h2>
                  <p>
                    Send an invitation to join your company as an employee.
                  </p>
                </div>
              </div>

              <InviteEmployeeForm
                onInvited={async () => {
                  setNotice("Invitation sent successfully.");
                  await loadTeamData();
                }}
              />
            </section>
          )}

          {activeTab === "invitations" && role === "admin" && (
            <section className="fx-panel">
              <div className="fx-panel-heading">
                <div>
                  <h2>Employee invitations</h2>
                  <p>Review invitation delivery and acceptance status.</p>
                </div>
                <span className="fx-count-pill">
                  {invitations.length} invitations
                </span>
              </div>

              {teamError && (
                <div className="fx-alert fx-alert-error" role="alert">
                  {teamError}
                </div>
              )}

              {teamLoading ? (
                <EmptyState>Loading invitations...</EmptyState>
              ) : invitations.length === 0 && !teamError ? (
                <EmptyState>
                  No invitations found.
                  <div style={{ marginTop: "1rem" }}>
                    <button
                      className="fx-button fx-button-primary"
                      onClick={() => setActiveTab("invite")}
                    >
                      Invite an employee
                    </button>
                  </div>
                </EmptyState>
              ) : (
                <div className="fx-table-wrap">
                  <table className="fx-table">
                    <thead>
                      <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Status</th>
                        <th>Sent</th>
                        <th>Expires</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {invitations.map((invitation) => {
                        const isDeleting =
                          String(deletingInvitationId) ===
                          String(invitation.id);

                        return (
                          <tr key={invitation.id}>
                            <td>{invitation.full_name || "—"}</td>
                            <td>{invitation.email}</td>
                            <td>
                              <span
                                className={`fx-status fx-status-${statusClass(
                                  invitation.status
                                )}`}
                              >
                                {invitation.status || "pending"}
                              </span>
                            </td>
                            <td>{formatDate(invitation.created_at)}</td>
                            <td>{formatDate(invitation.expires_at)}</td>
                            <td>
                              <button
                                type="button"
                                className="fx-button fx-button-small fx-button-danger"
                                disabled={isDeleting}
                                onClick={() =>
                                  handleDeleteInvitation(invitation)
                                }
                              >
                                {isDeleting ? "Deleting…" : "Delete"}
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
          )}

          {activeTab === "company" && role === "agent" && (
            <section className="fx-panel">
              <div className="fx-panel-heading">
                <div>
                  <h2>Company details</h2>
                  <p>Information currently available for your account.</p>
                </div>
              </div>

              <div className="fx-detail-grid">
                <div>
                  <span className="fx-detail-label">Company name</span>
                  <p>{user?.company_name || "Not available"}</p>
                </div>
                <div>
                  <span className="fx-detail-label">Your email</span>
                  <p>{user?.email || "—"}</p>
                </div>
                <div>
                  <span className="fx-detail-label">Role</span>
                  <p>Employee / Agent</p>
                </div>
              </div>
            </section>
          )}

          <footer className="fx-dashboard-footer">
            <span>© {new Date().getFullYear()} FixFlow</span>
            <span>AI-powered support workspace</span>
          </footer>
        </section>
      </div>
    </main>
  );
}