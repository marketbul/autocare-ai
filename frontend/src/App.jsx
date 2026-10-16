import { useCallback, useEffect, useState } from "react";
import { getToken, setToken } from "./api/client";
import { auth, owner } from "./api/diagnose";
import AuthScreen from "./screens/AuthScreen";
import { AskScreen, GarageScreen, HistoryScreen } from "./screens/OwnerScreens";
import { MyAdviceScreen, ShareAdviceScreen } from "./screens/MechanicScreens";
import { DamageScreen } from "./screens/DamageScreen";
import { AdminManuals, AdminNotes, AdminOverview, AdminUsers } from "./screens/AdminScreens";

const BASE = import.meta.env?.BASE_URL ?? "/app/";

const I = {
  chat: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16v11H9l-5 4V5z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /></svg>,
  car: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12l1.5-4.3A2 2 0 018.4 6.4h7.2a2 2 0 011.9 1.3L19 12M4 12h16v4.5a1 1 0 01-1 1H5a1 1 0 01-1-1V12z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /><circle cx="7.5" cy="14.8" r="1.1" fill="currentColor" /><circle cx="16.5" cy="14.8" r="1.1" fill="currentColor" /></svg>,
  clock: <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" strokeWidth="1.8" /><path d="M12 8v4.5l3 2" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /></svg>,
  wrench: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14.5 4.5a4.5 4.5 0 00-4.3 5.9L4 16.6 7.4 20l6.2-6.2a4.5 4.5 0 005.9-4.3l-2.7 2.7-2.9-.7-.7-2.9 2.7-2.7a4.5 4.5 0 00-1.4-.4z" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" /></svg>,
  list: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 7h11M8 12h11M8 17h11M4.5 7h.01M4.5 12h.01M4.5 17h.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" /></svg>,
  gauge: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 16a8 8 0 1116 0" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /><path d="M12 16l4-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" /></svg>,
  book: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 4h9a4 4 0 014 4v12H9a4 4 0 01-4-4V4z" fill="none" stroke="currentColor" strokeWidth="1.8" /><path d="M5 16a4 4 0 014-4h9" fill="none" stroke="currentColor" strokeWidth="1.8" /></svg>,
  check: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 3.5h9l3.5 3.5v13.5H6z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /><path d="M9 13.5l2.2 2.2L15.5 11" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>,
  users: <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="9" cy="8.5" r="3.2" fill="none" stroke="currentColor" strokeWidth="1.8" /><path d="M3.5 19a5.5 5.5 0 0111 0M15.5 5.6a3 3 0 010 5.8M17 14.2A5 5 0 0120.5 19" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /></svg>,
  dent: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3.5 15.5l2-5.2A2 2 0 017.4 9h9.2a2 2 0 011.9 1.3l2 5.2v2.5a1 1 0 01-1 1h-15a1 1 0 01-1-1v-2.5z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" /><path d="M9.5 12.5l1.6 1.4 1.4-2 1.5 1.6" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" /></svg>,
  out: <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 5h4a1 1 0 011 1v12a1 1 0 01-1 1h-4M10 16l-4-4 4-4M6 12h10" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" /></svg>,
};

// Navigation per role. An admin can also ask questions, to test the system.
const NAV = {
  owner: [
    { href: "#/ask", label: "Ask AutoCare", icon: I.chat },
    { href: "#/damage", label: "Damage check", icon: I.dent },
    { href: "#/cars", label: "My cars", icon: I.car },
    { href: "#/history", label: "History", icon: I.clock },
  ],
  mechanic: [
    { href: "#/advice/new", label: "Share advice", icon: I.wrench },
    { href: "#/advice", label: "My advice", icon: I.list },
  ],
  admin: [
    { href: "#/admin", label: "Overview", icon: I.gauge },
    { href: "#/admin/notes", label: "Mechanic notes", icon: I.check },
    { href: "#/admin/manuals", label: "Manuals & sources", icon: I.book },
    { href: "#/admin/users", label: "Users & roles", icon: I.users },
    { section: "Try it as an owner" },
    { href: "#/ask", label: "Ask AutoCare", icon: I.chat },
    { href: "#/damage", label: "Damage check", icon: I.dent },
    { href: "#/cars", label: "My cars", icon: I.car },
    { href: "#/history", label: "History", icon: I.clock },
  ],
};
const ROLE_LABEL = { owner: "Car owner", mechanic: "Mechanic", admin: "Admin" };

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

  // Restore a saved session.
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
    try { localStorage.setItem(vehicleKey(user), id); } catch { /* ignore */ }
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

  if (checking) return <div className="boot"><img src={`${BASE}emblem-256.jpg`} alt="" /></div>;
  if (!user) return <AuthScreen onSignedIn={signedIn} />;

  const nav = NAV[user.role];
  const allowed = nav.filter((n) => n.href).map((n) => n.href);
  const route = allowed.includes(hash) ? hash : nav[0].href;

  let screen;
  switch (route) {
    case "#/ask":
      screen = <AskScreen vehicles={vehicles} activeId={activeId} onPickVehicle={pickVehicle} go={go} initialQuery={askAgain} />;
      break;
    case "#/damage":
      screen = <DamageScreen vehicles={vehicles} activeId={activeId} onPickVehicle={pickVehicle} go={go} />;
      break;
    case "#/cars":
      screen = <GarageScreen vehicles={vehicles} reloadVehicles={reloadVehicles} activeId={activeId} onPickVehicle={pickVehicle} go={go} />;
      break;
    case "#/history":
      screen = <HistoryScreen vehicles={vehicles} onAskAgain={(c) => { pickVehicle(c.user_vehicle_id); if (c.kind === "damage") { go("#/damage"); return; } setAskAgain(c.question); go("#/ask"); }} />;
      break;
    case "#/advice/new": screen = <ShareAdviceScreen user={user} go={go} />; break;
    case "#/advice": screen = <MyAdviceScreen go={go} />; break;
    case "#/admin": screen = <AdminOverview go={go} />; break;
    case "#/admin/notes": screen = <AdminNotes />; break;
    case "#/admin/manuals": screen = <AdminManuals />; break;
    case "#/admin/users": screen = <AdminUsers me={user} />; break;
    default: screen = null;
  }

  return (
    <div className="shell">
      <aside className="rail">
        <a className="brand" href={nav[0].href}>
          <img src={`${BASE}emblem-256.jpg`} alt="" width="44" height="44" />
          <span><b>AutoCare AI</b><small>Connectivity & diagnostics</small></span>
        </a>
        <nav className="rail-nav" aria-label="Main">
          {nav.map((n, i) => n.section
            ? <p key={i} className="nav-heading">{n.section}</p>
            : <a key={n.href} href={n.href} className={`nav-item ${route === n.href ? "is-active" : ""}`}
                aria-current={route === n.href ? "page" : undefined}>{n.icon}<span>{n.label}</span></a>)}
        </nav>
        <div className="account">
          <span className="avatar" aria-hidden="true">{user.full_name.slice(0, 1).toUpperCase()}</span>
          <span className="account-who"><b>{user.full_name}</b><small>{ROLE_LABEL[user.role]}</small></span>
          <button className="icon-btn" onClick={signOut} title="Sign out" aria-label="Sign out">{I.out}</button>
        </div>
      </aside>

      <header className="topbar">
        <a className="brand" href={nav[0].href}><img src={`${BASE}emblem-256.jpg`} alt="" width="34" height="34" /></a>
        <nav className="topnav" aria-label="Main">
          {nav.filter((n) => n.href).map((n) => (
            <a key={n.href} href={n.href} className={route === n.href ? "is-active" : ""}>{n.label}</a>
          ))}
        </nav>
        <button className="icon-btn" onClick={signOut} aria-label="Sign out">{I.out}</button>
      </header>

      <main className="main" key={route}>{screen}</main>
    </div>
  );
}
