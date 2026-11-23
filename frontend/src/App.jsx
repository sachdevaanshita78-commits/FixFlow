
import { useEffect, useState } from "react";
import "./App.css";
import Dashboard from "./Dashboard";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

function navigate(path) {
  window.history.pushState({}, "", path);
  window.dispatchEvent(new PopStateEvent("popstate"));
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function LinkButton({ to, className = "", children, ...props }) {
  return (
    <a
      href={to}
      className={className}
      onClick={(event) => {
        if (
          event.button !== 0 ||
          event.metaKey ||
          event.ctrlKey ||
          event.shiftKey ||
          event.altKey
        ) {
          return;
        }

        event.preventDefault();
        navigate(to);
      }}
      {...props}
    >
      {children}
    </a>
  );
}

function Brand() {
  return (
    <LinkButton to="/" className="brand fixflow-brand">
      <span className="brand-icon brand-mark">F</span>
      <span className="brand-name">FixFlow</span>
    </LinkButton>
  );
}

function Header() {
  const [menuOpen, setMenuOpen] = useState(false);
  const closeMenu = () => setMenuOpen(false);

  return (
    <header className="navbar site-header">
      <div className="nav-inner">
        <Brand />

        <button
          type="button"
          className="mobile-menu-toggle"
          aria-label="Toggle navigation"
          aria-expanded={menuOpen}
          onClick={() => setMenuOpen(!menuOpen)}
        >
          {menuOpen ? "✕" : "☰"}
        </button>

        <nav className={`nav-links site-nav ${menuOpen ? "menu-open" : ""}`}>
          <a href="#platform" onClick={closeMenu}>Platform</a>
          <a href="#capabilities" onClick={closeMenu}>Capabilities</a>
          <a href="#how-it-works" onClick={closeMenu}>How it works</a>
          <a href="#security" onClick={closeMenu}>Security</a>
          <a href="#faq" onClick={closeMenu}>FAQs</a>
        </nav>

        <div className="nav-actions header-actions">
          <LinkButton
            to="/login"
            className="login-link"
            onClick={closeMenu}
          >
            Company login
          </LinkButton>
          <LinkButton
            to="/register"
            className="button primary-button"
            onClick={closeMenu}
          >
            Request access <span aria-hidden="true">↗</span>
          </LinkButton>
        </div>
      </div>
    </header>
  );
}

function SectionHeading({ eyebrow, title, description, light = false }) {
  return (
    <div className={`section-heading ${light ? "section-heading-light" : ""}`}>
      {eyebrow && <span className="eyebrow">{eyebrow}</span>}
      <h2>{title}</h2>
      {description && <p>{description}</p>}
    </div>
  );
}

function DashboardPreview() {
  return (
    <div
      className="dashboard-visual hero-visual"
      aria-label="Illustration of the FixFlow support dashboard"
    >
      <div className="dashboard-glow" />

      <div className="dashboard-preview">
        <div className="preview-top">
          <div className="preview-brand">
            <span className="preview-logo">F</span>
            <strong>FixFlow</strong>
          </div>
          <div className="preview-top-right">
            <span className="preview-live-dot" />
            <span>Workspace overview</span>
            <span className="preview-avatar">A</span>
          </div>
        </div>

        <div className="preview-body">
          <aside className="preview-sidebar">
            <span className="preview-sidebar-label">WORKSPACE</span>
            <div className="preview-menu preview-menu-active">
              <span>▦</span> Overview
            </div>
            <div className="preview-menu">
              <span>▤</span> All tickets
              <span className="preview-count">12</span>
            </div>
            <div className="preview-menu">
              <span>◷</span> My queue
            </div>
            <div className="preview-menu">
              <span>✧</span> AI drafts
            </div>
            <div className="preview-menu">
              <span>◉</span> Customers
            </div>

            <div className="preview-sidebar-bottom">
              <span className="preview-sidebar-label">YOUR TEAM</span>
              <div className="preview-team">
                <span className="team-avatar team-avatar-one">M</span>
                <span>Maya</span>
                <span className="team-online" />
              </div>
              <div className="preview-team">
                <span className="team-avatar team-avatar-two">J</span>
                <span>Jordan</span>
                <span className="team-online" />
              </div>
              <div className="preview-team">
                <span className="team-avatar team-avatar-three">S</span>
                <span>Sam</span>
              </div>
            </div>
          </aside>

          <div className="preview-main">
            <div className="preview-heading-row">
              <div>
                <span className="preview-muted">MONDAY, WORKSPACE OVERVIEW</span>
                <h3>Good morning, Alex <span>✦</span></h3>
                <p>Here's what's happening with your support team.</p>
              </div>
              <span className="preview-date">This week⌄</span>
            </div>

            <div className="preview-stats">
              <div className="preview-stat">
                <span>Open tickets</span>
                <strong>128</strong>
                <small className="stat-neutral">Across your workspace</small>
              </div>
              <div className="preview-stat">
                <span>Needs attention</span>
                <strong>08</strong>
                <small className="stat-warning">Priority queue</small>
              </div>
              <div className="preview-stat">
                <span>AI drafts ready</span>
                <strong>24</strong>
                <small className="stat-positive">Awaiting review</small>
              </div>
            </div>

            <div className="preview-ticket-heading">
              <div>
                <h4>Recent tickets</h4>
                <span>Illustrative workspace data</span>
              </div>
              <span className="preview-view-all">View all ↗</span>
            </div>

            <div className="ticket-card">
              <div className="ticket-icon ticket-icon-blue">↗</div>
              <div className="ticket-info">
                <strong>Unable to access my account</strong>
                <span>#TK-2048 · Customer support</span>
              </div>
              <span className="ticket-badge badge-priority">High</span>
              <span className="ticket-status status-progress">In progress</span>
            </div>

            <div className="ticket-card">
              <div className="ticket-icon ticket-icon-purple">✧</div>
              <div className="ticket-info">
                <strong>Question about my latest invoice</strong>
                <span>#TK-2047 · Billing</span>
              </div>
              <span className="ticket-badge badge-normal">Normal</span>
              <span className="ticket-status status-review">AI draft ready</span>
            </div>

            <div className="ticket-card">
              <div className="ticket-icon ticket-icon-green">✓</div>
              <div className="ticket-info">
                <strong>Update company contact details</strong>
                <span>#TK-2046 · Account management</span>
              </div>
              <span className="ticket-badge badge-normal">Normal</span>
              <span className="ticket-status status-resolved">Resolved</span>
            </div>

            <div className="preview-ai-note">
              <span className="preview-ai-icon">✧</span>
              <div>
                <strong>AI assistance, with your team in control</strong>
                <span>Review suggested responses before sending them.</span>
              </div>
              <span className="preview-note-arrow">↗</span>
            </div>
          </div>
        </div>
      </div>

      <div className="floating-note floating-note-top">
        <span className="floating-note-icon">✧</span>
        <div>
          <strong>AI-assisted workflow</strong>
          <span>Suggestions ready for review</span>
        </div>
      </div>

      <div className="floating-note floating-note-bottom">
        <span className="floating-check">✓</span>
        <div>
          <strong>One connected workspace</strong>
          <span>Tickets, teams and context</span>
        </div>
      </div>
    </div>
  );
}

function TrustStrip() {
  return (
    <section className="trust-strip" aria-label="Product principles">
      <p>Built around the way support teams work</p>
      <div className="trust-items">
        <span><i>✓</i> Structured ticket workflows</span>
        <span><i>✧</i> Human-reviewed AI assistance</span>
        <span><i>◈</i> Organization-based access</span>
        <span><i>↗</i> Operational visibility</span>
      </div>
    </section>
  );
}

const platformItems = [
  {
    number: "01",
    icon: "▦",
    title: "Organize",
    description:
      "Bring support requests into a structured workflow. Keep ticket details, priorities, ownership and progress visible in one place.",
    points: [
      "Centralized ticket inbox",
      "Clear ownership and status",
      "Consistent support workflows",
    ],
    color: "blue",
  },
  {
    number: "02",
    icon: "✧",
    title: "Assist",
    description:
      "Help agents understand requests and prepare responses with AI assistance, while keeping people responsible for the final decision.",
    points: [
      "Context-aware draft suggestions",
      "Less repetitive writing",
      "Human review before sending",
    ],
    color: "purple",
  },
  {
    number: "03",
    icon: "⌘",
    title: "Coordinate",
    description:
      "Give your team a shared view of customer issues, responsibilities and progress so that requests do not disappear between handoffs.",
    points: [
      "Shared team visibility",
      "Clear ticket handoffs",
      "Workspace-level insights",
    ],
    color: "green",
  },
];

function PlatformSection() {
  return (
    <section className="section platform-section" id="platform">
      <div className="section-container">
        <SectionHeading
          eyebrow="THE PLATFORM"
          title="Everything your support team needs. Connected."
          description="FixFlow brings the essential parts of customer support into one organized workspace, with AI assistance built into the workflow."
        />

        <div className="platform-grid">
          {platformItems.map((item) => (
            <article
              className={`platform-card platform-${item.color}`}
              key={item.number}
            >
              <div className="platform-card-top">
                <span className="platform-icon">{item.icon}</span>
                <span className="platform-number">{item.number}</span>
              </div>
              <h3>{item.title}</h3>
              <p>{item.description}</p>
              <ul>
                {item.points.map((point) => (
                  <li key={point}><span>✓</span>{point}</li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

const capabilities = [
  {
    icon: "▤",
    title: "Ticket management",
    description:
      "Keep requests, statuses, priorities and assigned team members organized from submission through resolution.",
  },
  {
    icon: "✧",
    title: "AI-assisted responses",
    description:
      "Give agents a starting point for replies with suggested drafts they can review, edit or reject.",
  },
  {
    icon: "◎",
    title: "Team collaboration",
    description:
      "Make ticket ownership and progress easier to understand, helping teams coordinate their work.",
  },
  {
    icon: "◷",
    title: "Operational insights",
    description:
      "Build visibility into support activity so teams can understand their workload and identify issues that need attention.",
  },
  {
    icon: "▧",
    title: "Knowledge and documents",
    description:
      "Keep relevant support documents available to help agents work with more consistent information.",
  },
  {
    icon: "◈",
    title: "Organization workspaces",
    description:
      "Structure users and support activity around their organization, with access governed by roles and permissions.",
  },
];

function CapabilitiesSection() {
  return (
    <section className="section capabilities-section" id="capabilities">
      <div className="section-container">
        <SectionHeading
          eyebrow="CORE CAPABILITIES"
          title="A more connected way to handle support"
          description="Move beyond scattered requests and disconnected tools. Give your team a clear process from the first ticket to the final resolution."
        />

        <div className="feature-grid">
          {capabilities.map((item, index) => (
            <article className="feature-card" key={item.title}>
              <div className={`feature-icon feature-icon-${index + 1}`}>
                {item.icon}
              </div>
              <h3>{item.title}</h3>
              <p>{item.description}</p>
              <span className="feature-index">
                {String(index + 1).padStart(2, "0")}
              </span>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

const onboardingSteps = [
  {
    number: "01",
    title: "Request organization access",
    description:
      "A company representative submits the organization's details and requests access to FixFlow.",
    icon: "↗",
  },
  {
    number: "02",
    title: "Complete the review",
    description:
      "The organization follows the platform's access and verification process before its workspace is approved.",
    icon: "◈",
  },
  {
    number: "03",
    title: "Set up your team",
    description:
      "Once access is granted, an authorized administrator can organize the workspace and invite team members.",
    icon: "⌘",
  },
  {
    number: "04",
    title: "Manage support together",
    description:
      "Your team can work with tickets, collaborate on requests and review AI-assisted drafts in the workspace.",
    icon: "✓",
  },
];

function WorkflowSection() {
  return (
    <section className="section workflow-section" id="how-it-works">
      <div className="section-container">
        <SectionHeading
          eyebrow="HOW IT WORKS"
          title="From organization request to a connected support team"
          description="A structured onboarding process helps organizations get set up with the right access and responsibilities."
        />

        <div className="workflow-grid">
          {onboardingSteps.map((step, index) => (
            <article className="workflow-step" key={step.number}>
              <div className="workflow-step-top">
                <span className="workflow-number">{step.number}</span>
                <span className="workflow-icon">{step.icon}</span>
              </div>
              {index < onboardingSteps.length - 1 && (
                <div className="workflow-connector" aria-hidden="true">→</div>
              )}
              <h3>{step.title}</h3>
              <p>{step.description}</p>
            </article>
          ))}
        </div>

        <div className="workflow-callout">
          <div className="workflow-callout-icon">i</div>
          <p>
            <strong>Access is organization-based.</strong> Requesting access
            starts the process; it does not automatically create an approved
            company workspace.
          </p>
          <LinkButton to="/register" className="text-link">
            Request access ↗
          </LinkButton>
        </div>
      </div>
    </section>
  );
}

function BusinessSection() {
  return (
    <section className="section business-section" id="organizations">
      <div className="section-container business-layout">
        <div className="business-copy">
          <span className="eyebrow">MADE FOR ORGANIZATIONS</span>
          <h2>
            Your company's support operations, in one dedicated workspace.
          </h2>
          <p>
            FixFlow is designed around teams and organizations rather than
            disconnected individual accounts. Access is managed through
            organization membership, roles and permissions.
          </p>

          <div className="business-benefits">
            <div className="business-benefit">
              <span>✓</span>
              <div>
                <strong>Organization-led access</strong>
                <p>Workspace access follows the organization's onboarding process.</p>
              </div>
            </div>
            <div className="business-benefit">
              <span>✓</span>
              <div>
                <strong>Administrator-managed invitations</strong>
                <p>Authorized administrators can invite teammates into their workspace.</p>
              </div>
            </div>
            <div className="business-benefit">
              <span>✓</span>
              <div>
                <strong>Role-aware collaboration</strong>
                <p>Permissions help determine what each workspace member can do.</p>
              </div>
            </div>
          </div>

          <LinkButton to="/register" className="button primary-button">
            Request organization access ↗
          </LinkButton>
        </div>

        <div className="organization-visual">
          <div className="organization-card">
            <div className="organization-card-heading">
              <div>
                <span className="organization-label">WORKSPACE STRUCTURE</span>
                <h3>Acme Support Team</h3>
              </div>
              <span className="organization-status">Workspace</span>
            </div>

            <div className="organization-owner">
              <span className="organization-avatar organization-avatar-admin">A</span>
              <div>
                <strong>Workspace administrator</strong>
                <span>Manages members and access</span>
              </div>
              <span className="role-pill">Admin</span>
            </div>

            <div className="organization-divider" />

            <div className="organization-members-heading">
              <strong>Team members</strong>
              <span>Example structure</span>
            </div>

            <div className="organization-member">
              <span className="organization-avatar organization-avatar-agent">M</span>
              <div>
                <strong>Support agent</strong>
                <span>Handles assigned requests</span>
              </div>
              <span className="member-check">✓</span>
            </div>

            <div className="organization-member">
              <span className="organization-avatar organization-avatar-agent-two">J</span>
              <div>
                <strong>Support agent</strong>
                <span>Reviews and resolves tickets</span>
              </div>
              <span className="member-check">✓</span>
            </div>

            <div className="organization-member">
              <span className="organization-avatar organization-avatar-agent-three">S</span>
              <div>
                <strong>Support agent</strong>
                <span>Collaborates with the team</span>
              </div>
              <span className="member-check">✓</span>
            </div>

            <div className="organization-security-note">
              <span>◈</span>
              Members and permissions are managed within the workspace.
            </div>
          </div>
          <span className="organization-decoration organization-decoration-one" />
          <span className="organization-decoration organization-decoration-two" />
        </div>
      </div>
    </section>
  );
}

function SecuritySection() {
  const principles = [
    {
      icon: "◈",
      title: "Organization-aware access",
      description:
        "Workspace access should be enforced by backend authorization and organization membership, not just by what the interface displays.",
    },
    {
      icon: "⌑",
      title: "Role-based permissions",
      description:
        "Different roles can be assigned different responsibilities and permitted actions.",
    },
    {
      icon: "✧",
      title: "AI with human oversight",
      description:
        "AI-generated reply suggestions are drafts for people to review, not automatic customer messages.",
    },
    {
      icon: "▤",
      title: "Accountability and visibility",
      description:
        "A structured workflow makes ticket ownership and support activity easier to follow.",
    },
  ];

  return (
    <section className="section security-section" id="security">
      <div className="section-container">
        <div className="security-panel">
          <div className="security-intro">
            <span className="eyebrow">SECURITY & CONTROL</span>
            <h2>AI assistance should never mean losing control.</h2>
            <p>
              FixFlow's design centers on organization-aware access,
              permissions and human oversight. Security depends on the
              backend enforcing these rules on every relevant request.
            </p>
            <LinkButton to="/register" className="security-link">
              Explore organization access ↗
            </LinkButton>
          </div>

          <div className="security-grid">
            {principles.map((item) => (
              <article className="security-item" key={item.title}>
                <span className="security-icon">{item.icon}</span>
                <h3>{item.title}</h3>
                <p>{item.description}</p>
              </article>
            ))}
          </div>
        </div>

        <p className="security-footnote">
          Security note: these are product design principles, not a claim of
          certification or a guarantee of compliance. Actual isolation and
          permissions must be implemented and tested in the backend.
        </p>
      </div>
    </section>
  );
}

const faqs = [
  {
    question: "Who is FixFlow designed for?",
    answer:
      "FixFlow is designed for businesses and organizations that manage customer support requests with a team. It brings ticket organization, team coordination and AI-assisted response drafting into one workspace.",
  },
  {
    question: "Can any individual create a company workspace?",
    answer:
      "Not automatically. A company representative can request organization access, but submitting a request does not itself create an approved workspace. Access follows the platform's organization review and onboarding process.",
  },
  {
    question: "How do support agents join a company?",
    answer:
      "An authorized administrator can invite team members to the organization's workspace. The invited person follows the invitation process to join. Membership and permissions should be validated by the backend.",
  },
  {
    question: "Does FixFlow use AI to send replies automatically?",
    answer:
      "The intended workflow is human-reviewed AI assistance. FixFlow can help prepare a suggested response, but the agent reviews and edits the draft before sending it. An AI suggestion should not be treated as a message that has already been sent.",
  },
  {
    question: "Is each company's information separated?",
    answer:
      "FixFlow is designed around organization-based workspaces. Proper separation depends on backend-enforced tenant isolation, authorization checks and data-access controls on every relevant operation. A frontend-only restriction is not sufficient to guarantee isolation.",
  },
];

function FAQSection() {
  const [openIndex, setOpenIndex] = useState(0);

  return (
    <section className="section faq-section" id="faq">
      <div className="section-container faq-layout">
        <div className="faq-intro">
          <span className="eyebrow">FREQUENTLY ASKED QUESTIONS</span>
          <h2>Good questions. Clear answers.</h2>
          <p>
            Learn how FixFlow workspaces, team invitations and AI-assisted
            support are intended to work.
          </p>
          <p className="faq-contact">
            Still have questions?{" "}
            <a href="mailto:hello@fixflow.example">Contact our team</a>
          </p>
        </div>

        <div className="faq-list">
          {faqs.map((faq, index) => {
            const isOpen = openIndex === index;
            const answerId = `faq-answer-${index}`;

            return (
              <article
                className={`faq-item ${isOpen ? "faq-item-open" : ""}`}
                key={faq.question}
              >
                <button
                  type="button"
                  className="faq-question"
                  aria-expanded={isOpen}
                  aria-controls={answerId}
                  onClick={() => setOpenIndex(isOpen ? -1 : index)}
                >
                  <span className="faq-number">
                    {String(index + 1).padStart(2, "0")}
                  </span>
                  <span>{faq.question}</span>
                  <span className="faq-toggle" aria-hidden="true">
                    {isOpen ? "−" : "+"}
                  </span>
                </button>

                {isOpen && (
                  <div className="faq-answer" id={answerId}>
                    <p>{faq.answer}</p>
                  </div>
                )}
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function FinalCTA() {
  return (
    <section className="final-cta">
      <div className="final-cta-decoration final-cta-decoration-one" />
      <div className="final-cta-decoration final-cta-decoration-two" />

      <div className="final-cta-content">
        <span className="eyebrow">READY TO GET ORGANIZED?</span>
        <h2>Give your support team a better way to work.</h2>
        <p>
          Bring your tickets, team workflows and AI-assisted drafts into one
          connected workspace.
        </p>
        <div className="final-cta-actions">
          <LinkButton to="/register" className="button cta-button-light">
            Request organization access <span>↗</span>
          </LinkButton>
          <LinkButton to="/login" className="button cta-button-outline">
            Company login
          </LinkButton>
        </div>
        <span className="final-cta-note">
          Organization-based access · Human-reviewed AI assistance
        </span>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="footer site-footer">
      <div className="footer-main">
        <div className="footer-brand-column">
          <Brand />
          <p>
            A connected workspace for customer support teams. Organize
            requests, coordinate people and work with AI-assisted drafts.
          </p>
        </div>

        <div className="footer-column">
          <h4>Product</h4>
          <a href="#platform">Platform</a>
          <a href="#capabilities">Capabilities</a>
          <a href="#how-it-works">How it works</a>
          <a href="#security">Security</a>
        </div>

        <div className="footer-column">
          <h4>Get started</h4>
          <LinkButton to="/register">Request access</LinkButton>
          <LinkButton to="/login">Company login</LinkButton>
          <a href="#faq">FAQs</a>
        </div>

        <div className="footer-column">
          <h4>Contact</h4>
          <a href="mailto:hello@fixflow.example">Email our team</a>
          <span>Organization onboarding</span>
          <span>Support workflows</span>
        </div>
      </div>

      <div className="footer-bottom">
        <span>© {new Date().getFullYear()} FixFlow. All rights reserved.</span>
        <span className="footer-bottom-note">
          Built for organized, human-centered support.
        </span>
        <a
          href="#top"
          onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
        >
          Back to top ↑
        </a>
      </div>
    </footer>
  );
}

function HomePage() {
  useEffect(() => {
    document.title = "FixFlow — Customer Support, Connected";
  }, []);

  return (
    <div className="site" id="top">
      <Header />

      <main>
        <section className="hero hero-section">
          <div className="hero-container">
            <div className="hero-copy hero-content">
              <span className="eyebrow hero-eyebrow">
                <span className="eyebrow-dot" />
                CUSTOMER SUPPORT, REIMAGINED
              </span>

              <h1>
                Support that flows.
                <br />
                <span>Work that moves.</span>
              </h1>

              <p className="hero-description">
                FixFlow gives your support team one connected place to manage
                tickets, coordinate work and create AI-assisted responses —
                with people firmly in control.
              </p>

              <div className="hero-actions">
                <LinkButton to="/register" className="button primary-button">
                  Request organization access <span>↗</span>
                </LinkButton>
                <a href="#platform" className="button secondary-button">
                  Explore the platform <span>↓</span>
                </a>
              </div>

              <div className="hero-note">
                <span className="hero-note-icon">◈</span>
                <span>Organization-based workspaces</span>
                <span className="hero-note-divider">·</span>
                <span>Human-reviewed AI drafts</span>
              </div>

              <div className="hero-proof">
                <div className="hero-proof-avatars" aria-hidden="true">
                  <span>A</span><span>M</span><span>J</span><span>+</span>
                </div>
                <p>
                  <strong>One connected workflow.</strong>
                  <br />
                  From incoming requests to team resolution.
                </p>
              </div>
            </div>

            <DashboardPreview />
          </div>

          <div className="hero-bottom-glow" />
        </section>

        <TrustStrip />
        <PlatformSection />
        <CapabilitiesSection />
        <WorkflowSection />
        <BusinessSection />
        <SecuritySection />
        <FAQSection />
        <FinalCTA />
      </main>

      <Footer />
    </div>
  );
}

function AuthLayout({ title, subtitle, children }) {
  return (
    <div className="auth-page">
      <div className="auth-topbar">
        <Brand />
        <LinkButton to="/" className="auth-home-link">
          ← Back to homepage
        </LinkButton>
      </div>

      <main className="auth-main">
        <section className="auth-card">
          <div className="auth-header">
            <span className="auth-logo">F</span>
            <span className="eyebrow">FIXFLOW WORKSPACE</span>
            <h1>{title}</h1>
            <p>{subtitle}</p>
          </div>

          {children}
        </section>

        <p className="auth-bottom-note">
          Organization-based access · Human-reviewed AI assistance
        </p>
      </main>

      <footer className="auth-footer">
        <span>© {new Date().getFullYear()} FixFlow</span>
        <LinkButton to="/">Home</LinkButton>
      </footer>
    </div>
  );
}

function Message({ type = "error", children }) {
  if (!children) return null;

  return (
    <div
      className={`auth-message ${type === "success" ? "message-success" : "message-error"}`}
      role={type === "error" ? "alert" : "status"}
    >
      {children}
    </div>
  );
}

// Password validation shared by organization registration and invitations.
function getPasswordChecks(password) {
  return {
    length: password.length >= 12 && password.length <= 128,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /[0-9]/.test(password),
    special: /[^A-Za-z0-9\s]/.test(password),
    noSpaces: password.length > 0 && !/\s/.test(password),
  };
}

function PasswordRequirements({ password }) {
  const checks = getPasswordChecks(password);

  const requirements = [
    { key: "length", label: "12–128 characters" },
    { key: "uppercase", label: "At least one uppercase letter (A–Z)" },
    { key: "lowercase", label: "At least one lowercase letter (a–z)" },
    { key: "number", label: "At least one number (0–9)" },
    {
      key: "special",
      label: "At least one special character (e.g. !@#$%)",
    },
    { key: "noSpaces", label: "No spaces in the password" },
  ];

  const isValid = Object.values(checks).every(Boolean);

  return (
    <div className="password-requirements" aria-live="polite">
      <p className="password-requirements-title">
        Password requirements
      </p>

      <ul>
        {requirements.map((requirement) => {
          const passed = checks[requirement.key];

          return (
            <li
              key={requirement.key}
              className={
                passed ? "requirement-passed" : "requirement-pending"
              }
            >
              <span className="requirement-icon" aria-hidden="true">
                {passed ? "✓" : "○"}
              </span>
              <span>{requirement.label}</span>
            </li>
          );
        })}
      </ul>

      <p className={isValid ? "password-valid" : "password-incomplete"}>
        {isValid
          ? "✓ Your password meets all requirements."
          : "Complete all requirements to continue."}
      </p>
    </div>
  );
}

function PasswordToggle({ showPassword, onToggle }) {
  return (
    <button
      type="button"
      className="password-toggle"
      onClick={onToggle}
      aria-label={showPassword ? "Hide password" : "Show password"}
    >
      {showPassword ? "Hide" : "Show"}
    </button>
  );
}

function RegisterPage() {
  const [companyName, setCompanyName] = useState("");
  const [adminName, setAdminName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("error");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const passwordValid = Object.values(getPasswordChecks(password)).every(
    Boolean
  );

  useEffect(() => {
    document.title = "Request organization access — FixFlow";
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    setMessage("");

    if (!passwordValid) {
      setMessageType("error");
      setMessage("Please meet all password requirements before continuing.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        `${API_BASE}/auth/register-organization`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            company_name: companyName.trim(),
            admin_name: adminName.trim(),
            email: email.trim(),
            password,
          }),
        }
      );

      const data = await response.json().catch(() => ({}));

      if (response.status === 404 || response.status === 405) {
        throw new Error(
          "The organization registration endpoint is unavailable. Check POST /api/v1/auth/register-organization in the backend."
        );
      }

      if (!response.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((item) => item.msg).join(", ")
          : data.detail;

        throw new Error(detail || "Unable to submit your request.");
      }

      setMessageType("success");
      setMessage(
        data.message ||
          "Your organization access request was submitted successfully. The platform administrator must review it before your workspace is created."
      );
      setPassword("");
    } catch (error) {
      setMessageType("error");
      setMessage(
        error.message ||
          "Unable to connect to the server. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout
      title="Request organization access"
      subtitle="Tell us about your company to begin the FixFlow onboarding process."
    >
      <form className="auth-form" onSubmit={handleSubmit}>
        <Message type={messageType}>{message}</Message>

        <div className="auth-info-banner">
          <span>◈</span>
          <p>
            Submitting this form requests access. It does not automatically
            approve or create a company workspace.
          </p>
        </div>

        <label htmlFor="company-name">
          Company or organization name
        </label>
        <input
          id="company-name"
          type="text"
          autoComplete="organization"
          placeholder="Your company name"
          minLength={2}
          maxLength={120}
          value={companyName}
          onChange={(event) => setCompanyName(event.target.value)}
          required
        />

        <label htmlFor="admin-name">Your full name</label>
        <input
          id="admin-name"
          type="text"
          autoComplete="name"
          placeholder="Enter your full name"
          minLength={2}
          maxLength={120}
          value={adminName}
          onChange={(event) => setAdminName(event.target.value)}
          required
        />

        <label htmlFor="register-email">Work email</label>
        <input
          id="register-email"
          type="email"
          autoComplete="email"
          placeholder="you@company.com"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
        />

        <label htmlFor="register-password">Create a password</label>
        <div className="password-input-wrap">
          <input
            id="register-password"
            type={showPassword ? "text" : "password"}
            autoComplete="new-password"
            placeholder="Create a strong password"
            minLength={12}
            maxLength={128}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            aria-describedby="register-password-requirements"
            required
          />
          <PasswordToggle
            showPassword={showPassword}
            onToggle={() => setShowPassword((current) => !current)}
          />
        </div>

        <div id="register-password-requirements">
          <PasswordRequirements password={password} />
        </div>

        <button
          className="button primary-button auth-submit"
          type="submit"
          disabled={loading || !passwordValid}
        >
          {loading ? "Submitting request..." : "Submit access request"}
          {!loading && <span>↗</span>}
        </button>

        <p className="auth-switch">
          Already have an account?{" "}
          <LinkButton to="/login">Company login</LinkButton>
        </p>
      </form>
    </AuthLayout>
  );
}

function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("error");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    document.title = "Company login — FixFlow";
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    setMessage("");
    setLoading(true);

    try {
      const formData = new URLSearchParams();
      formData.set("username", email.trim());
      formData.set("password", password);

      const response = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData.toString(),
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(
          data.detail || "Login failed. Check your credentials and try again."
        );
      }

      if (!data.access_token) {
        throw new Error("The server did not return an access token.");
      }

      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("token_type", data.token_type || "bearer");

      const userResponse = await fetch(`${API_BASE}/auth/me`, {
        headers: {
          Authorization: `Bearer ${data.access_token}`,
        },
      });

      const user = await userResponse.json().catch(() => ({}));

      if (!userResponse.ok) {
        throw new Error(
          user.detail ||
            "Login succeeded, but user details could not be loaded. Check that GET /api/v1/auth/me exists."
        );
      }

      if (!user.role) {
        throw new Error("The user details response does not contain a role.");
      }

      const dashboardPaths = {
        platform_admin: "/platform-dashboard",
        admin: "/company-dashboard",
        agent: "/employee-dashboard",
      };

      const destination = dashboardPaths[user.role];

      if (!destination) {
        throw new Error(`Unsupported account role: ${user.role}`);
      }

      localStorage.setItem("user", JSON.stringify(user));
      navigate(destination);
    } catch (error) {
      setMessageType("error");
      setMessage(
        error.message ||
          "Unable to connect to FixFlow. Check that the backend is running."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Sign in to access your organization's FixFlow workspace."
    >
      <form className="auth-form" onSubmit={handleSubmit}>
        <Message type={messageType}>{message}</Message>

        <label htmlFor="login-email">Work email</label>
        <input
          id="login-email"
          type="email"
          name="email"
          autoComplete="username"
          placeholder="you@company.com"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
        />

        <div className="password-label-row">
          <label htmlFor="login-password">Password</label>
        </div>

        <div className="password-input-wrap">
          <input
            id="login-password"
            type={showPassword ? "text" : "password"}
            name="password"
            autoComplete="current-password"
            placeholder="Enter your password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
          <PasswordToggle
            showPassword={showPassword}
            onToggle={() => setShowPassword((current) => !current)}
          />
        </div>

        <button
          className="button primary-button auth-submit"
          type="submit"
          disabled={loading}
        >
          {loading ? "Signing in..." : "Sign in to FixFlow"}
          {!loading && <span>↗</span>}
        </button>

        <p className="auth-switch">
          Need organization access?{" "}
          <LinkButton to="/register">Request access</LinkButton>
        </p>
      </form>
    </AuthLayout>
  );
}

function AcceptInvitationPage() {
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("error");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const token = new URLSearchParams(window.location.search).get("token");

  const passwordValid = Object.values(getPasswordChecks(password)).every(
    Boolean
  );

  useEffect(() => {
    document.title = "Accept invitation — FixFlow";
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();
    setMessage("");

    if (!passwordValid) {
      setMessageType("error");
      setMessage("Please meet all password requirements before continuing.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/invitations/accept`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          token,
          full_name: fullName.trim(),
          password,
        }),
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((item) => item.msg).join(", ")
          : data.detail;

        throw new Error(detail || "Unable to accept this invitation.");
      }

      setMessageType("success");
      setMessage(
        data.message ||
          "Invitation accepted. You can now try signing in to your workspace."
      );
      setPassword("");
    } catch (error) {
      setMessageType("error");
      setMessage(
        error.message ||
          "Unable to connect to the server. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout
      title="Join your team"
      subtitle="Complete your account setup to join your organization's workspace."
    >
      {!token ? (
        <div className="auth-form">
          <Message>
            This invitation link does not contain an invitation token. Open
            the complete invitation link sent to you by your administrator.
          </Message>
          <LinkButton to="/" className="button primary-button auth-submit">
            Return to homepage
          </LinkButton>
        </div>
      ) : (
        <form className="auth-form" onSubmit={handleSubmit}>
          <Message type={messageType}>{message}</Message>

          <label htmlFor="invite-full-name">Full name</label>
          <input
            id="invite-full-name"
            type="text"
            autoComplete="name"
            placeholder="Enter your full name"
            minLength={2}
            maxLength={120}
            value={fullName}
            onChange={(event) => setFullName(event.target.value)}
            required
          />

          <label htmlFor="invite-password">Create a password</label>
          <div className="password-input-wrap">
            <input
              id="invite-password"
              type={showPassword ? "text" : "password"}
              autoComplete="new-password"
              placeholder="Create a strong password"
              minLength={12}
              maxLength={128}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              aria-describedby="invite-password-requirements"
              required
            />
            <PasswordToggle
              showPassword={showPassword}
              onToggle={() => setShowPassword((current) => !current)}
            />
          </div>

          <div id="invite-password-requirements">
            <PasswordRequirements password={password} />
          </div>

          <button
            className="button primary-button auth-submit"
            type="submit"
            disabled={loading || !passwordValid}
          >
            {loading ? "Accepting invitation..." : "Accept invitation"}
            {!loading && <span>↗</span>}
          </button>

          <p className="auth-switch">
            Already a member?{" "}
            <LinkButton to="/login">Sign in</LinkButton>
          </p>
        </form>
      )}
    </AuthLayout>
  );
}

const DASHBOARD_PATHS = [
  "/platform-dashboard",
  "/company-dashboard",
  "/employee-dashboard",
];

export default function App() {
  const [pathname, setPathname] = useState(window.location.pathname);

  useEffect(() => {
    const handleLocationChange = () => {
      setPathname(window.location.pathname);
    };

    window.addEventListener("popstate", handleLocationChange);

    return () => {
      window.removeEventListener("popstate", handleLocationChange);
    };
  }, []);

  useEffect(() => {
    if (DASHBOARD_PATHS.includes(pathname)) {
      document.title = "Dashboard — FixFlow";
    }
  }, [pathname]);

  if (pathname === "/login") return <LoginPage />;
  if (pathname === "/register") return <RegisterPage />;
  if (pathname === "/accept-invitation") return <AcceptInvitationPage />;

  if (DASHBOARD_PATHS.includes(pathname)) {
    return <Dashboard onNavigate={navigate} />;
  }

  return <HomePage />;
}
