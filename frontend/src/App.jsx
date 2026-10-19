import { useCallback, useEffect, useState } from "react";
import { getToken, setToken } from "./api/client";
import { auth, owner } from "./api/diagnose";
import AuthScreen from "./screens/AuthScreen";
import { AskScreen, GarageScreen, HistoryScreen } from "./screens/OwnerScreens";
import { MyAdviceScreen, ShareAdviceScreen } from "./screens/MechanicScreens";
import { DamageScreen } from "./screens/DamageScreen";
import { VerifyScreen } from "./screens/VerifyScreen";
import { HealthScreen } from "./screens/HealthScreen";
import { SimilarCasesScreen } from "./screens/SimilarCasesScreen";
import { AdminManuals, AdminNotes, AdminOverview, AdminUsers } from "./screens/AdminScreens";
import { GraphScreen } from "./screens/GraphScreen";
import { PricingScreen } from "./screens/PricingScreen";
import { ModelAnalyticsScreen } from "./screens/ModelAnalyticsScreen";
import { CorpusScreen } from "./screens/CorpusScreen";
import { BentoDashboardScreen } from "./screens/BentoDashboardScreen";
import { SettingsScreen } from "./screens/SettingsScreen";

const BASE = import.meta.env?.BASE_URL ?? "/app/";

const I = {
  bento: <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="7" height="7" rx="2" stroke="currentColor" strokeWidth="1.8" fill="none" /><rect x="14" y="3" width="7" height="4" rx="1.5" stroke="currentColor" strokeWidth="1.8" fill="none" /><rect x="14" y="10" width="7" height="11" rx="2" stroke="currentColor" strokeWidth="1.8" fill="none" /><rect x="3" y="13" width="7" height="8" rx="2" stroke="currentColor" strokeWidth="1.8" fill="none" /></svg>,
  chat: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16v11H9l-5 4V5z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /></svg>,
  car: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12l1.5-4.3A2 2 0 018.4 6.4h7.2a2 2 0 011.9 1.3L19 12M4 12h16v4.5a1 1 0 01-1 1H5a1 1 0 01-1-1V12z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /><circle cx="7.5" cy="14.8" r="1.1" fill="currentColor" /><circle cx="16.5" cy="14.8" r="1.1" fill="currentColor" /></svg>,
  clock: <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" strokeWidth="1.8" /><path d="M12 8v4.5l3 2" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /></svg>,
  wrench: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14.5 4.5a4.5 4.5 0 00-4.3 5.9L4 16.6 7.4 20l6.2-6.2a4.5 4.5 0 005.9-4.3l-2.7 2.7-2.9-.7-.7-2.9 2.7-2.7a4.5 4.5 0 00-1.4-.4z" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" /></svg>,
  list: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 7h11M8 12h11M8 17h11M4.5 7h.01M4.5 12h.01M4.5 17h.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" /></svg>,
  gauge: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 16a8 8 0 1116 0" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /><path d="M12 16l4-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" /></svg>,
  book: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 4h9a4 4 0 014 4v12H9a4 4 0 01-4-4V4z" fill="none" stroke="currentColor" strokeWidth="1.8" /><path d="M5 16a4 4 0 014-4h9" fill="none" stroke="currentColor" strokeWidth="1.8" /></svg>,
  check: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 3.5h9l3.5 3.5v13.5H6z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /><path d="M9 13.5l2.2 2.2L15.5 11" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>,
  users: <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="9" cy="8.5" r="3.2" fill="none" stroke="currentColor" strokeWidth="1.8" /><path d="M3.5 19a5.5 5.5 0 0111 0M15.5 5.6a3 3 0 010 5.8M17 14.2A5 5 0 0120.5 19" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /></svg>,
  tag: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /><circle cx="7" cy="7" r="1.5" fill="currentColor" /></svg>,
  graph: <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="6" cy="6" r="2.5" fill="none" stroke="currentColor" strokeWidth="1.8" /><circle cx="18" cy="6" r="2.5" fill="none" stroke="currentColor" strokeWidth="1.8" /><circle cx="12" cy="18" r="2.5" fill="none" stroke="currentColor" strokeWidth="1.8" /><path d="M7.8 7.8l3.4 8.4M16.2 7.8l-3.4 8.4M8.5 6h7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" /></svg>,
  chart: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M18 20V10M12 20V4M6 20v-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>,
  corpus: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 19.5A2.5 2.5 0 016.5 17H20M4 4.5A2.5 2.5 0 016.5 2H20v20H6.5a2.5 2.5 0 01-2.5-2.5v-15z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /><path d="M8 7h8M8 11h6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /></svg>,
  settings: <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>,
  out: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 5h4a1 1 0 011 1v12a1 1 0 01-1 1h-4M10 16l-4-4 4-4M6 12h10" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></svg>,
  sun: <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>,
  moon: <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>,
};

const NAV = {
  owner: [
    { href: "#/dashboard", label: "Dashboard", icon: I.bento, badge: "Live" },
    { href: "#/ask", label: "Ask AI Copilot", icon: I.chat, badge: "AI" },
    { href: "#/cars", label: "My Garage", icon: I.car },
    { href: "#/health", label: "Health & Telemetry", icon: I.gauge },
    { href: "#/pricing", label: "Parts & Quotes", icon: I.tag, badge: "PKR" },
    { href: "#/history", label: "Diagnostic History", icon: I.clock },
    { href: "#/settings", label: "Settings", icon: I.settings },
  ],
  mechanic: [
    { href: "#/advice/new", label: "Share Advice", icon: I.wrench },
    { href: "#/advice", label: "My Advice", icon: I.list },
    { href: "#/pricing", label: "Parts & Quotes", icon: I.tag, badge: "PKR" },
    { href: "#/settings", label: "Settings", icon: I.settings },
  ],
  admin: [
    { href: "#/dashboard", label: "Executive Dashboard", icon: I.bento },
    { href: "#/admin", label: "System Overview", icon: I.gauge },
    { href: "#/admin/notes", label: "Mechanic Notes", icon: I.check },
    { href: "#/admin/manuals", label: "Manuals & Vector Store", icon: I.book },
    { href: "#/admin/users", label: "Users & Roles", icon: I.users },
    { section: "Advanced AI Tools" },
    { href: "#/graph", label: "Causal Graph", icon: I.graph },
    { href: "#/analytics", label: "Model Analytics", icon: I.chart },
    { href: "#/settings", label: "Settings", icon: I.settings },
  ],
};

const ROLE_LABEL = { owner: "Car Owner", mechanic: "Mechanic", admin: "Administrator" };

function useHash() {
  const [hash, setHash] = useState(() => window.location.hash || "");
  useEffect(() => {
    const on = () => setHash(window.location.hash || "");
    window.addEventListener("hashchange", on);
    return () => window.removeEventListener("hashchange", on);
  }, []);
  const go = useCallback((h) => { window.location.hash = h; }, []);
  return [hash, go];
}

const vehicleKey = (u) => `autocare.vehicle.${u.user_id}`;
const readActive = (u) => { try { return localStorage.getItem(vehicleKey(u)) || ""; } catch { return ""; } };

export default function App() {
  const [user, setUser] = useState(null);
  const [checking, setChecking] = useState(Boolean(getToken()));
  const [hash, go] = useHash();
  const [vehicles, setVehicles] = useState([]);
  const [activeId, setActiveId] = useState("");
  const [askAgain, setAskAgain] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  
  // Theme State
  const [theme, setTheme] = useState(() => {
    try { return localStorage.getItem("autocare_theme") || "dark"; } catch { return "dark"; }
  });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    try { localStorage.setItem("autocare_theme", theme); } catch {}
  }, [theme]);

  const toggleTheme = useCallback(() => {
    setTheme((t) => (t === "dark" ? "light" : "dark"));
  }, []);

  // Restore saved session
  useEffect(() => {
    if (!getToken()) return;
    auth.me().then(setUser).catch(() => setToken(null)).finally(() => setChecking(false));
  }, []);

  useEffect(() => {
    const out = () => { setToken(null); setUser(null); };
    window.addEventListener("autocare:signed-out", out);
    return () => window.removeEventListener("autocare:signed-out", out);
  }, []);

  const canOwn = Boolean(user && (user.role === "owner" || user.role === "admin"));
  const reloadVehicles = useCallback(async () => {
    if (!canOwn) return [];
    const list = await owner.vehicles();
    setVehicles(list);
    setActiveId((cur) => {
      const keep = list.some((v) => v.user_vehicle_id === cur) ? cur : readActive(user);
      return list.some((v) => v.user_vehicle_id === keep) ? keep : list[0]?.user_vehicle_id || "";
    });
    return list;
  }, [canOwn, user]);

  useEffect(() => { reloadVehicles().catch(() => {}); }, [reloadVehicles]);

  function pickVehicle(id) {
    setActiveId(id);
    try { localStorage.setItem(vehicleKey(user), id); } catch {}
  }

  function signedIn({ token, user: u }) {
    setToken(token);
    setUser(u);
    go(NAV[u.role][0].href);
  }

  function signOut() {
    setToken(null);
    setUser(null);
    setVehicles([]);
    go("#/");
  }

  function handleQuickSearch(e) {
    if (e.key === "Enter" && searchQuery.trim()) {
      setAskAgain(searchQuery.trim());
      setSearchQuery("");
      go("#/ask");
    }
  }

  if (checking) {
    return (
      <div className="boot">
        <div className="boot-spinner" />
        <img src={`${BASE}emblem-256.jpg`} alt="AutoCare AI" width="48" height="48" />
        <span>Loading AutoCare AI Telemetry...</span>
      </div>
    );
  }

  if (!user) {
    return <AuthScreen onSignedIn={signedIn} theme={theme} onToggleTheme={toggleTheme} />;
  }

  const nav = NAV[user.role] || NAV.owner;
  const allowed = nav.filter((n) => n.href).map((n) => n.href);
  const route = (allowed.includes(hash) || ["#/settings", "#/graph", "#/pricing", "#/analytics", "#/corpus", "#/verify", "#/similar", "#/damage"].includes(hash))
    ? hash : nav[0].href;

  const currentNav = nav.find((n) => n.href === route);
  const activeVehicle = vehicles.find((v) => v.user_vehicle_id === activeId);

  let screen;
  switch (route) {
    case "#/dashboard":
      screen = <BentoDashboardScreen go={go} />;
      break;
    case "#/ask":
      screen = <AskScreen vehicles={vehicles} activeId={activeId} onPickVehicle={pickVehicle} go={go} initialQuery={askAgain} />;
      break;
    case "#/cars":
      screen = <GarageScreen vehicles={vehicles} reloadVehicles={reloadVehicles} activeId={activeId} onPickVehicle={pickVehicle} go={go} />;
      break;
    case "#/health":
      screen = <HealthScreen vehicles={vehicles} activeId={activeId} onPickVehicle={pickVehicle} go={go} />;
      break;
    case "#/pricing":
      screen = <PricingScreen />;
      break;
    case "#/history":
      screen = <HistoryScreen vehicles={vehicles} onAskAgain={(c) => { pickVehicle(c.user_vehicle_id); if (c.kind === "damage") { go("#/damage"); return; } setAskAgain(c.question); go("#/ask"); }} />;
      break;
    case "#/settings":
      screen = <SettingsScreen user={user} theme={theme} onToggleTheme={toggleTheme} go={go} />;
      break;
    case "#/verify":
      screen = <VerifyScreen vehicles={vehicles} activeId={activeId} onPickVehicle={pickVehicle} go={go} />;
      break;
    case "#/similar":
      screen = <SimilarCasesScreen vehicles={vehicles} activeId={activeId} onPickVehicle={pickVehicle} go={go} />;
      break;
    case "#/damage":
      screen = <DamageScreen vehicles={vehicles} activeId={activeId} onPickVehicle={pickVehicle} go={go} />;
      break;
    case "#/graph":
      screen = <GraphScreen />;
      break;
    case "#/analytics":
      screen = <ModelAnalyticsScreen />;
      break;
    case "#/corpus":
      screen = <CorpusScreen />;
      break;
    case "#/advice/new": screen = <ShareAdviceScreen user={user} go={go} />; break;
    case "#/advice": screen = <MyAdviceScreen go={go} />; break;
    case "#/admin": screen = <AdminOverview go={go} />; break;
    case "#/admin/notes": screen = <AdminNotes />; break;
    case "#/admin/manuals": screen = <AdminManuals />; break;
    case "#/admin/users": screen = <AdminUsers me={user} />; break;
    default: screen = <BentoDashboardScreen go={go} />;
  }

  return (
    <div className="shell">
      {/* Sleek Modern Sidebar */}
      <aside className="rail">
        <a className="brand" href={nav[0].href}>
          <div className="brand-logo-frame">
            <img src={`${BASE}emblem-256.jpg`} alt="AutoCare AI" width="30" height="30" />
          </div>
          <div>
            <b>AutoCare AI</b>
            <small>Diagnostics Co-Pilot</small>
          </div>
        </a>

        {/* Workspace Mode Badge */}
        <div className="workspace-badge">
          <span className="live-dot" />
          <span>PUCIT Telemetry Node</span>
        </div>

        <nav className="rail-nav" aria-label="Main Navigation">
          {nav.map((n, i) => n.section
            ? <p key={i} className="nav-heading">{n.section}</p>
            : (
              <a
                key={n.href}
                href={n.href}
                className={`nav-item ${route === n.href ? "is-active" : ""}`}
                aria-current={route === n.href ? "page" : undefined}
              >
                {n.icon}
                <span style={{ flex: 1 }}>{n.label}</span>
                {n.badge && <span className="nav-badge">{n.badge}</span>}
              </a>
            ))}
        </nav>

        {/* Sidebar Footer User Card */}
        <div className="account">
          <span className="avatar" aria-hidden="true">
            {user.full_name.slice(0, 1).toUpperCase()}
          </span>
          <div className="account-who">
            <b>{user.full_name}</b>
            <small>{ROLE_LABEL[user.role]}</small>
          </div>
          <button className="icon-btn" onClick={signOut} title="Sign out" aria-label="Sign out">
            {I.out}
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="content-shell">
        {/* Sleek Top Navigation Header Bar */}
        <header className="desktop-topbar">
          <div className="topbar-left">
            <div className="breadcrumb">
              <span className="breadcrumb-root">AutoCare AI</span>
              <span className="breadcrumb-sep">/</span>
              <span className="breadcrumb-current">{currentNav?.label || "Workspace"}</span>
            </div>

            {/* Active Monitored Vehicle Quick Pill */}
            {activeVehicle && (
              <div className="active-car-pill" onClick={() => go("#/cars")} title="Switch or edit vehicle">
                <span className="car-pulse-dot" />
                <span><b>{activeVehicle.label}</b></span>
                <span className="pill-divider">&bull;</span>
                <span style={{ color: "var(--text-muted)" }}>{activeVehicle.current_mileage ? `${activeVehicle.current_mileage.toLocaleString()} km` : "Telemetry Active"}</span>
              </div>
            )}
          </div>

          <div className="topbar-right">
            {/* Quick AI Command Search */}
            <div className="topbar-search">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8"/>
                <line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
              <input
                type="text"
                placeholder="Ask AI or search DTC (e.g. P0217)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={handleQuickSearch}
              />
              <span className="search-shortcut">↵ Enter</span>
            </div>

            {/* Theme Toggle Button in Topbar */}
            <button
              type="button"
              className="topbar-theme-btn"
              onClick={toggleTheme}
              title={`Switch to ${theme === "dark" ? "Light" : "Dark"} mode`}
            >
              {theme === "dark" ? I.sun : I.moon}
            </button>

            {/* User Profile Mini Badge */}
            <div className="topbar-user" onClick={() => go("#/settings")}>
              <span className="topbar-avatar">{user.full_name.slice(0, 1).toUpperCase()}</span>
              <span className="topbar-username">{user.full_name}</span>
            </div>
          </div>
        </header>

        {/* Screen Content */}
        <main className="main" key={route}>{screen}</main>
      </div>
    </div>
  );
}
