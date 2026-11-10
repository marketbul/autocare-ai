AI AUTO PAKISTAN - FACEBOOK COMMUNITY Q&A LOCAL DROP FOLDER
===========================================================

Use this folder to import real public Facebook automotive page questions &
solutions into your local offline dataset (no web port needed).

HOW TO ADD FACEBOOK COMMUNITY Q&As:
1. Open `facebook_qa_input.csv` in Excel, Google Sheets, or any text editor
   (or save your own `.csv`, `.json`, or `.jsonl` file inside this folder).
2. Add rows of public automotive questions & mechanic/community solutions.
   - Full columns (already in `facebook_qa_input.csv`):
     source_url,post_date,make,model,variant,manufacturing_year,problem_title,
     problem_description,symptoms,proposed_solution,estimated_cost_pkr,city,
     evidence_quote,review_status
   - Quick CSV minimum (if saving a quick sheet):
     Just `problem_title` (or `question`) + `problem_description` +
     `proposed_solution` (plus optional `make`, `model`, `source_url`, `city`).
     Vehicle make/model (`Toyota Corolla`, `Suzuki Alto`, `Honda Civic`, etc.),
     fault category, Urdu/Roman Urdu language, and PKR cost are detected
     automatically, and phone numbers / CNICs / emails are redacted for privacy.
3. Double-click `import_facebook_qa.bat` in the project root folder!
   It cleans, deduplicates, categorizes, rebuilds ML splits, exports:
     AI_Auto_Pakistan_Dataset/facebook_qa_solutions.json
     AI_Auto_Pakistan_Dataset/master_dataset.{json,jsonl,csv}
   and opens `AI_Auto_Pakistan_Dataset/dataset_viewer.html` offline (`file:///`).

NOTE ON ETHICS & VERIFICATION:
- Only copy public automotive page Q&A discussions you are authorized to research.
- Do not include private groups or personal phone numbers.
- Rows default to `verification_status="unverified"` unless marked `approved`.
