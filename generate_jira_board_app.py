import os
import csv
import json
import shutil

def generate_jira_board_html():
    base_dir = r"C:\Users\ABDUL\.gemini\antigravity\scratch\autocare-us2"
    csv_path = os.path.join(base_dir, "docs", "jira_tickets_import.csv")
    desktop_dir = r"C:\Users\ABDUL\Desktop"
    deliverable_dir = r"C:\Users\ABDUL\Desktop\AutoCare_AI_Complete_Deliverable_2026-11-10"

    tickets = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            tickets.append({
                "key": r.get("Issue key", ""),
                "type": r.get("Issue Type", "Story"),
                "summary": r.get("Summary", ""),
                "desc": r.get("Description", ""),
                "epic": r.get("Epic Link", ""),
                "sp": int(r.get("Story Points", 3) or 3),
                "assignee": r.get("Assignee", ""),
                "priority": r.get("Priority", "Medium"),
                "status": r.get("Status", "Done"),
                "sprint": r.get("Sprint", ""),
                "commit_hash": r.get("Commit Hash", ""),
                "commit_msg": r.get("Git Commit Message", ""),
                "date": r.get("Resolved Date", "")
            })

    tickets_json = json.dumps(tickets)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AutoCare AI — Jira Software Agile Board (Key: AUT)</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
      background-color: #0d1117;
      color: #c9d1d9;
    }}
    .jira-column {{
      min-width: 290px;
      max-width: 320px;
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 8px;
    }}
    .jira-card {{
      background: #21262d;
      border: 1px solid #30363d;
      border-radius: 6px;
      transition: all 0.15s ease-in-out;
      cursor: pointer;
    }}
    .jira-card:hover {{
      border-color: #58a6ff;
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    }}
    .badge-story {{ background: #1f6feb; color: white; }}
    .badge-bug {{ background: #f85149; color: white; }}
    .badge-task {{ background: #238636; color: white; }}
    .custom-scrollbar::-webkit-scrollbar {{
      width: 6px;
      height: 6px;
    }}
    .custom-scrollbar::-webkit-scrollbar-thumb {{
      background: #30363d;
      border-radius: 4px;
    }}
  </style>
</head>
<body class="min-h-screen flex flex-col">

  <!-- TOP JIRA NAVIGATION BAR -->
  <header class="bg-[#161b22] border-b border-[#30363d] px-6 py-3 flex items-center justify-between sticky top-0 z-50">
    <div class="flex items-center space-x-4">
      <div class="flex items-center space-x-2 text-blue-400 font-bold text-lg">
        <i class="fa-brands fa-jira text-2xl text-blue-500"></i>
        <span class="tracking-wide text-white">Jira Software</span>
        <span class="text-xs px-2 py-0.5 rounded bg-blue-900/60 text-blue-300 font-mono">AUT Board</span>
      </div>
      <div class="h-5 w-px bg-gray-700"></div>
      <div class="text-sm font-semibold text-gray-200 flex items-center space-x-2">
        <span class="text-gray-400">Projects /</span>
        <span class="hover:underline cursor-pointer">AutoCare AI (AUT)</span>
      </div>
      <span class="text-xs bg-emerald-900/60 text-emerald-300 px-2.5 py-0.5 rounded-full border border-emerald-700 font-medium">
        Active Scrum • 138 Tickets
      </span>
    </div>

    <div class="flex items-center space-x-4 text-sm">
      <div class="flex items-center space-x-1 text-gray-400">
        <span class="text-xs">University:</span>
        <span class="text-white font-medium">PUCIT BS Data Science</span>
      </div>
      <a href="https://github.com/marketbul/autocare-ai.git" target="_blank" class="flex items-center space-x-1 bg-[#21262d] hover:bg-[#30363d] text-white px-3 py-1.5 rounded-md border border-[#30363d] transition">
        <i class="fa-brands fa-github"></i>
        <span class="text-xs font-semibold">GitHub Repo</span>
      </a>
    </div>
  </header>

  <!-- SUBHEADER: FILTERS & STATS -->
  <div class="bg-[#0d1117] border-b border-[#30363d] px-6 py-3 flex flex-wrap items-center justify-between gap-3">
    <div class="flex flex-wrap items-center gap-3">
      <!-- Search Input -->
      <div class="relative">
        <i class="fa-solid fa-magnifying-glass absolute left-3 top-2.5 text-gray-400 text-xs"></i>
        <input type="text" id="searchInput" placeholder="Search ticket or commit..." 
          class="bg-[#161b22] border border-[#30363d] text-xs text-gray-200 pl-8 pr-3 py-1.5 rounded-md focus:outline-none focus:border-blue-500 w-56">
      </div>

      <!-- Assignee Filter -->
      <select id="assigneeFilter" class="bg-[#161b22] border border-[#30363d] text-xs text-gray-200 px-3 py-1.5 rounded-md focus:outline-none focus:border-blue-500">
        <option value="ALL">All 5 Members</option>
        <option value="Abdullah">Abdullah (035) - Architect & RAG</option>
        <option value="Talha">Talha Ali Bhatti (016) - Storage & Kafka</option>
        <option value="Danial">Danial Hameed (014) - Data & Corpus</option>
        <option value="Ahmad">Ahmad Zahid (033) - Triage & Safety</option>
        <option value="Muhammad Abdullah">Muhammad Abdullah (032) - Web & Analytics</option>
      </select>

      <!-- Sprint Filter -->
      <select id="sprintFilter" class="bg-[#161b22] border border-[#30363d] text-xs text-gray-200 px-3 py-1.5 rounded-md focus:outline-none focus:border-blue-500">
        <option value="ALL">All Sprints (1 to 6)</option>
        <option value="Sprint 1">Sprint 1 (Architecture & Taxonomy)</option>
        <option value="Sprint 2">Sprint 2 (Triage ML & Calibration)</option>
        <option value="Sprint 3">Sprint 3 (Causal Graph & Verifier)</option>
        <option value="Sprint 4">Sprint 4 (Dataset Scaling & RAG)</option>
        <option value="Sprint 5">Sprint 5 (Future Big Data Lake)</option>
        <option value="Sprint 6">Sprint 6 (Future PySpark Analytics)</option>
      </select>

      <!-- Quick Reset -->
      <button onclick="resetFilters()" class="text-xs text-blue-400 hover:text-blue-300 font-semibold px-2 py-1">
        Reset
      </button>
    </div>

    <!-- Quick Stats -->
    <div class="flex items-center space-x-3 text-xs">
      <div class="bg-[#161b22] px-3 py-1 rounded border border-[#30363d] text-gray-300">
        Total: <span id="statTotal" class="font-bold text-white">138</span>
      </div>
      <div class="bg-emerald-950/60 px-3 py-1 rounded border border-emerald-800 text-emerald-300">
        Completed: <span id="statDone" class="font-bold">124</span>
      </div>
      <div class="bg-blue-950/60 px-3 py-1 rounded border border-blue-800 text-blue-300">
        Future Backlog: <span id="statTodo" class="font-bold">14</span>
      </div>
      <div class="bg-purple-950/60 px-3 py-1 rounded border border-purple-800 text-purple-300">
        Velocity: <span id="statPoints" class="font-bold">535 SP</span>
      </div>
    </div>
  </div>

  <!-- JIRA KANBAN COLUMNS CONTAINER -->
  <main class="flex-1 overflow-x-auto p-6 custom-scrollbar">
    <div class="flex items-start space-x-4 min-h-[750px]">

      <!-- COLUMN: BACKLOG / REFINED -->
      <div class="jira-column flex flex-col flex-shrink-0">
        <div class="px-3 py-2.5 border-b border-[#30363d] flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <span class="text-xs font-bold text-gray-300 uppercase tracking-wider">Backlog</span>
            <span id="count-backlog" class="text-[10px] bg-gray-700 text-gray-300 px-2 py-0.5 rounded-full font-bold">0</span>
          </div>
          <i class="fa-solid fa-list-check text-gray-500 text-xs"></i>
        </div>
        <div id="col-backlog" class="p-2 space-y-2 flex-1 overflow-y-auto max-h-[720px] custom-scrollbar"></div>
      </div>

      <!-- COLUMN: TO DO (FUTURE BIG DATA) -->
      <div class="jira-column flex flex-col flex-shrink-0">
        <div class="px-3 py-2.5 border-b border-[#30363d] flex items-center justify-between bg-blue-950/20">
          <div class="flex items-center space-x-2">
            <span class="text-xs font-bold text-blue-400 uppercase tracking-wider">To Do (Big Data S5-S6)</span>
            <span id="count-todo" class="text-[10px] bg-blue-900 text-blue-200 px-2 py-0.5 rounded-full font-bold">14</span>
          </div>
          <i class="fa-solid fa-clock text-blue-400 text-xs"></i>
        </div>
        <div id="col-todo" class="p-2 space-y-2 flex-1 overflow-y-auto max-h-[720px] custom-scrollbar"></div>
      </div>

      <!-- COLUMN: IN PROGRESS -->
      <div class="jira-column flex flex-col flex-shrink-0">
        <div class="px-3 py-2.5 border-b border-[#30363d] flex items-center justify-between bg-amber-950/20">
          <div class="flex items-center space-x-2">
            <span class="text-xs font-bold text-amber-400 uppercase tracking-wider">In Progress</span>
            <span id="count-inprogress" class="text-[10px] bg-amber-900 text-amber-200 px-2 py-0.5 rounded-full font-bold">0</span>
          </div>
          <i class="fa-solid fa-spinner text-amber-400 text-xs"></i>
        </div>
        <div id="col-inprogress" class="p-2 space-y-2 flex-1 overflow-y-auto max-h-[720px] custom-scrollbar"></div>
      </div>

      <!-- COLUMN: CODE REVIEW / QA -->
      <div class="jira-column flex flex-col flex-shrink-0">
        <div class="px-3 py-2.5 border-b border-[#30363d] flex items-center justify-between bg-purple-950/20">
          <div class="flex items-center space-x-2">
            <span class="text-xs font-bold text-purple-400 uppercase tracking-wider">Code Review / QA</span>
            <span id="count-review" class="text-[10px] bg-purple-900 text-purple-200 px-2 py-0.5 rounded-full font-bold">0</span>
          </div>
          <i class="fa-solid fa-code-pull-request text-purple-400 text-xs"></i>
        </div>
        <div id="col-review" class="p-2 space-y-2 flex-1 overflow-y-auto max-h-[720px] custom-scrollbar"></div>
      </div>

      <!-- COLUMN: DONE (124 VERIFIED COMMITS) -->
      <div class="jira-column flex flex-col flex-shrink-0 border-emerald-900/50">
        <div class="px-3 py-2.5 border-b border-[#30363d] flex items-center justify-between bg-emerald-950/30">
          <div class="flex items-center space-x-2">
            <span class="text-xs font-bold text-emerald-400 uppercase tracking-wider">Done (Verified in Git)</span>
            <span id="count-done" class="text-[10px] bg-emerald-800 text-emerald-100 px-2 py-0.5 rounded-full font-bold">124</span>
          </div>
          <i class="fa-solid fa-circle-check text-emerald-400 text-xs"></i>
        </div>
        <div id="col-done" class="p-2 space-y-2 flex-1 overflow-y-auto max-h-[720px] custom-scrollbar"></div>
      </div>

    </div>
  </main>

  <!-- DETAIL MODAL -->
  <div id="ticketModal" class="fixed inset-0 bg-black/75 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
    <div class="bg-[#161b22] border border-[#30363d] rounded-xl max-w-xl w-full p-6 shadow-2xl relative">
      <button onclick="closeModal()" class="absolute right-4 top-4 text-gray-400 hover:text-white">
        <i class="fa-solid fa-xmark text-lg"></i>
      </button>

      <div class="flex items-center space-x-2 mb-3">
        <span id="modalTypeBadge" class="text-xs px-2 py-0.5 rounded font-bold uppercase">Story</span>
        <span id="modalKey" class="text-xs text-blue-400 font-mono font-bold">AUT-101</span>
        <span class="text-gray-600">•</span>
        <span id="modalSprint" class="text-xs text-gray-400">Sprint 1</span>
      </div>

      <h3 id="modalTitle" class="text-lg font-bold text-white mb-3">Ticket Title</h3>

      <div class="space-y-3 text-xs text-gray-300">
        <div class="bg-[#0d1117] p-3 rounded border border-[#30363d]">
          <div class="font-semibold text-gray-400 mb-1">Description:</div>
          <div id="modalDesc">Detailed description here...</div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div class="bg-[#0d1117] p-2.5 rounded border border-[#30363d]">
            <span class="text-gray-400 block mb-0.5">Assignee:</span>
            <span id="modalAssignee" class="font-bold text-white">Member Name</span>
          </div>
          <div class="bg-[#0d1117] p-2.5 rounded border border-[#30363d]">
            <span class="text-gray-400 block mb-0.5">Story Points:</span>
            <span id="modalPoints" class="font-bold text-purple-300">5 SP</span>
          </div>
        </div>

        <div class="bg-[#0d1117] p-3 rounded border border-[#30363d]">
          <span class="text-gray-400 block mb-1">Git Commit Linkage:</span>
          <div class="flex items-center space-x-2">
            <span id="modalCommitHash" class="font-mono bg-gray-800 text-blue-400 px-2 py-0.5 rounded text-[11px]">8b3275c</span>
            <span id="modalCommitMsg" class="font-mono text-gray-400 truncate text-[11px]">commit message</span>
          </div>
        </div>

        <div class="bg-[#0d1117] p-2.5 rounded border border-[#30363d] flex items-center justify-between">
          <span class="text-gray-400">Epic:</span>
          <span id="modalEpic" class="font-semibold text-emerald-400">EPIC-1</span>
        </div>
      </div>

      <div class="mt-5 pt-3 border-t border-[#30363d] flex justify-end">
        <button onclick="closeModal()" class="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold rounded">
          Close Ticket
        </button>
      </div>
    </div>
  </div>

  <script>
    const MASTER_TICKETS = {tickets_json};

    function renderBoard() {{
      const search = document.getElementById('searchInput').value.toLowerCase();
      const assignee = document.getElementById('assigneeFilter').value;
      const sprint = document.getElementById('sprintFilter').value;

      const colBacklog = document.getElementById('col-backlog');
      const colTodo = document.getElementById('col-todo');
      const colInProgress = document.getElementById('col-inprogress');
      const colReview = document.getElementById('col-review');
      const colDone = document.getElementById('col-done');

      colBacklog.innerHTML = '';
      colTodo.innerHTML = '';
      colInProgress.innerHTML = '';
      colReview.innerHTML = '';
      colDone.innerHTML = '';

      let cBacklog = 0, cTodo = 0, cInProgress = 0, cReview = 0, cDone = 0;
      let visiblePoints = 0;

      MASTER_TICKETS.forEach(t => {{
        // Match Search
        const matchesSearch = t.key.toLowerCase().includes(search) || 
                              t.summary.toLowerCase().includes(search) ||
                              t.commit_msg.toLowerCase().includes(search) ||
                              t.commit_hash.toLowerCase().includes(search);
        // Match Assignee
        const matchesAssignee = (assignee === 'ALL') || t.assignee.toLowerCase().includes(assignee.toLowerCase());
        // Match Sprint
        const matchesSprint = (sprint === 'ALL') || t.sprint.toLowerCase().includes(sprint.toLowerCase());

        if (matchesSearch && matchesAssignee && matchesSprint) {{
          visiblePoints += t.sp;
          const card = createCard(t);

          if (t.status === 'Done') {{
            colDone.appendChild(card);
            cDone++;
          }} else if (t.status === 'To Do') {{
            colTodo.appendChild(card);
            cTodo++;
          }} else if (t.status === 'In Progress') {{
            colInProgress.appendChild(card);
            cInProgress++;
          }} else if (t.status === 'Code Review') {{
            colReview.appendChild(card);
            cReview++;
          }} else {{
            colBacklog.appendChild(card);
            cBacklog++;
          }}
        }}
      }});

      document.getElementById('count-backlog').innerText = cBacklog;
      document.getElementById('count-todo').innerText = cTodo;
      document.getElementById('count-inprogress').innerText = cInProgress;
      document.getElementById('count-review').innerText = cReview;
      document.getElementById('count-done').innerText = cDone;

      document.getElementById('statTotal').innerText = (cBacklog + cTodo + cInProgress + cReview + cDone);
      document.getElementById('statDone').innerText = cDone;
      document.getElementById('statTodo').innerText = cTodo;
      document.getElementById('statPoints').innerText = visiblePoints + ' SP';
    }}

    function createCard(t) {{
      const div = document.createElement('div');
      div.className = 'jira-card p-3';
      div.onclick = () => openModal(t);

      const typeBadgeClass = t.type === 'Bug' ? 'badge-bug' : (t.type === 'Test' ? 'badge-task' : 'badge-story');
      const hashText = t.commit_hash !== 'PLANNED' ? `[${{t.commit_hash}}]` : '[PLANNED]';
      const shortAssignee = t.assignee.split(' ')[0];

      div.innerHTML = `
        <div class="flex items-center justify-between mb-1.5">
          <span class="text-[10px] px-1.5 py-0.5 rounded font-bold uppercase ${{typeBadgeClass}}">${{t.type}}</span>
          <span class="text-[11px] font-mono text-blue-400 font-bold">${{t.key}}</span>
        </div>
        <div class="text-xs font-semibold text-gray-200 mb-2 line-clamp-2 leading-snug">
          ${{t.summary}}
        </div>
        <div class="flex items-center justify-between text-[11px] text-gray-400 pt-2 border-t border-[#30363d]/60">
          <span class="truncate max-w-[130px] font-medium text-gray-300">
            <i class="fa-solid fa-user-circle text-gray-500 mr-1"></i>${{shortAssignee}}
          </span>
          <div class="flex items-center space-x-1.5">
            <span class="font-mono text-[10px] text-gray-500">${{hashText}}</span>
            <span class="px-1.5 py-0.2 rounded bg-purple-950/60 text-purple-300 font-bold text-[10px] border border-purple-800">${{t.sp}}</span>
          </div>
        </div>
      `;
      return div;
    }}

    function openModal(t) {{
      document.getElementById('modalKey').innerText = t.key;
      document.getElementById('modalTypeBadge').innerText = t.type;
      document.getElementById('modalTypeBadge').className = `text-xs px-2 py-0.5 rounded font-bold uppercase ${{t.type === 'Bug' ? 'badge-bug' : (t.type === 'Test' ? 'badge-task' : 'badge-story')}}`;
      document.getElementById('modalSprint').innerText = t.sprint;
      document.getElementById('modalTitle').innerText = t.summary;
      document.getElementById('modalDesc').innerText = t.desc;
      document.getElementById('modalAssignee').innerText = t.assignee;
      document.getElementById('modalPoints').innerText = t.sp + ' Story Points';
      document.getElementById('modalCommitHash').innerText = t.commit_hash;
      document.getElementById('modalCommitMsg').innerText = t.commit_msg;
      document.getElementById('modalEpic').innerText = t.epic;

      document.getElementById('ticketModal').classList.remove('hidden');
    }}

    function closeModal() {{
      document.getElementById('ticketModal').classList.add('hidden');
    }}

    function resetFilters() {{
      document.getElementById('searchInput').value = '';
      document.getElementById('assigneeFilter').value = 'ALL';
      document.getElementById('sprintFilter').value = 'ALL';
      renderBoard();
    }}

    document.getElementById('searchInput').addEventListener('input', renderBoard);
    document.getElementById('assigneeFilter').addEventListener('change', renderBoard);
    document.getElementById('sprintFilter').addEventListener('change', renderBoard);

    // Initial render
    renderBoard();
  </script>
</body>
</html>
"""

    html_path = os.path.join(base_dir, "JIRA_LOCAL_BOARD.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[OK] Generated Interactive Jira App: {html_path}")

    # Create Batch Launchers
    bat_content = """@echo off
title AutoCare AI - Jira Agile Board Launcher
echo ======================================================================
echo           Opening AutoCare AI Jira Software Agile Board
echo ======================================================================
echo.
echo [INFO] Launching interactive Jira Kanban Board in your default browser...
start "" "%~dp0JIRA_LOCAL_BOARD.html"
echo.
echo [SUCCESS] Jira Board opened! Showing all 138 Tickets & Git Commits.
echo.
"""
    bat_path = os.path.join(base_dir, "OPEN_JIRA_APP.bat")
    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(bat_content)

    # Sync to Desktop and Desktop Deliverables
    shutil.copy2(html_path, os.path.join(desktop_dir, "JIRA_LOCAL_BOARD.html"))
    shutil.copy2(bat_path, os.path.join(desktop_dir, "OPEN_JIRA_APP.bat"))
    shutil.copy2(html_path, os.path.join(deliverable_dir, "JIRA_LOCAL_BOARD.html"))
    shutil.copy2(bat_path, os.path.join(deliverable_dir, "OPEN_JIRA_APP.bat"))

    print("[SYNC] Copied JIRA_LOCAL_BOARD.html and OPEN_JIRA_APP.bat to Desktop and Deliverables!")

if __name__ == "__main__":
    generate_jira_board_html()
