import os
import shutil

chat_dir = r"C:\Users\ABDUL\Desktop\AutoCare_AI_Complete_Deliverable_2026-11-10\chat_history"
root_dir = r"C:\Users\ABDUL\Desktop\AutoCare_AI_Complete_Deliverable_2026-11-10"

# Read existing HTML
src_html = os.path.join(chat_dir, "CHAT_HISTORY_EXPORT.html")
if os.path.exists(src_html):
    with open(src_html, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Update headers to prominently state "Automotive Dataset Engineer"
    updated_html = html_content.replace(
        "<title>AutoCare AI — Shareable Chat History (89 Turns)</title>",
        "<title>Automotive Dataset Engineer — Multi-Source Automotive Data Engineering Session</title>"
    ).replace(
        "AutoCare AI — Shareable Engineering Chat History",
        "Automotive Dataset Engineer — Complete Multi-Source Automotive Data Collection &amp; Engineering Session"
    ).replace(
        "Engineering conversation session with zero API key leaks",
        "Session Name: Automotive Dataset Engineer | Engineering conversation log with zero API key leaks"
    )

    dst_html = os.path.join(chat_dir, "Automotive_Dataset_Engineer_Chat_History.html")
    with open(dst_html, "w", encoding="utf-8") as f:
        f.write(updated_html)
    print("Created Automotive_Dataset_Engineer_Chat_History.html")

    # Overwrite the original as well so both are updated
    with open(src_html, "w", encoding="utf-8") as f:
        f.write(updated_html)

# Read existing Markdown
src_md = os.path.join(chat_dir, "CHAT_HISTORY_EXPORT.md")
if os.path.exists(src_md):
    with open(src_md, "r", encoding="utf-8") as f:
        md_content = f.read()

    updated_md = md_content.replace(
        "# AutoCare AI — Shareable Engineering Chat History",
        "# Automotive Dataset Engineer — Multi-Source Automotive Data Engineering Session"
    )

    dst_md = os.path.join(chat_dir, "Automotive_Dataset_Engineer_Chat_History.md")
    with open(dst_md, "w", encoding="utf-8") as f:
        f.write(updated_md)
    print("Created Automotive_Dataset_Engineer_Chat_History.md")

# Copy jsonl transcript with clear name
src_jsonl = os.path.join(chat_dir, "chat_transcript_redacted.jsonl")
if os.path.exists(src_jsonl):
    dst_jsonl = os.path.join(chat_dir, "Automotive_Dataset_Engineer_Transcript.jsonl")
    shutil.copy2(src_jsonl, dst_jsonl)
    print("Created Automotive_Dataset_Engineer_Transcript.jsonl")

# Create batch files in root for one-click access
bat_chat = os.path.join(root_dir, "OPEN_AUTOMOTIVE_DATASET_ENGINEER_CHAT.bat")
with open(bat_chat, "w", encoding="utf-8") as f:
    f.write('@echo off\r\nstart "" "%~dp0chat_history\\Automotive_Dataset_Engineer_Chat_History.html"\r\n')
print("Created OPEN_AUTOMOTIVE_DATASET_ENGINEER_CHAT.bat")

bat_dataset = os.path.join(root_dir, "OPEN_DATASET_FOLDER.bat")
with open(bat_dataset, "w", encoding="utf-8") as f:
    f.write('@echo off\r\nexplorer "%~dp0dataset"\r\n')
print("Created OPEN_DATASET_FOLDER.bat")

bat_pid = os.path.join(root_dir, "OPEN_BIG_DATA_PID.bat")
with open(bat_pid, "w", encoding="utf-8") as f:
    f.write('@echo off\r\nstart "" "%~dp0Big_Data_PID_AutoData_Lake_4Weeks.pdf"\r\n')
print("Created OPEN_BIG_DATA_PID.bat")
