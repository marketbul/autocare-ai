import os
import shutil

src_pkg = r"C:\Users\ABDUL\.gemini\antigravity\scratch\autocare-us2\backend\autocare\rag_scratch"
dst_pkg = r"C:\Users\ABDUL\Desktop\AutoCare_AI_Complete_Deliverable_2026-11-10\backend\autocare\rag_scratch"

if os.path.exists(dst_pkg):
    shutil.rmtree(dst_pkg)
shutil.copytree(src_pkg, dst_pkg)
print("Copied rag_scratch package to Desktop deliverable")

src_demo = r"C:\Users\ABDUL\.gemini\antigravity\scratch\autocare-us2\backend\run_rag_demo.py"
dst_demo = r"C:\Users\ABDUL\Desktop\AutoCare_AI_Complete_Deliverable_2026-11-10\backend\run_rag_demo.py"
shutil.copy2(src_demo, dst_demo)
print("Copied run_rag_demo.py to Desktop deliverable")

bat_path = r"C:\Users\ABDUL\Desktop\AutoCare_AI_Complete_Deliverable_2026-11-10\RUN_RAG_FROM_SCRATCH_DEMO.bat"
with open(bat_path, "w", encoding="utf-8") as f:
    f.write('@echo off\r\ncd /d "%~dp0backend"\r\npython run_rag_demo.py\r\npause\r\n')
print("Created RUN_RAG_FROM_SCRATCH_DEMO.bat")
