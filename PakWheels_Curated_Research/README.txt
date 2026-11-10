AI AUTO PAKISTAN - PAKWHEELS CURATED RESEARCH DROP FOLDER
========================================================

PakWheels Terms of Service & robots.txt prohibit automated scraping of
pakwheels.com/forums and /technical-auto-help/.

How PakWheels data is included cleanly:
1. Official YouTube API (`PakWheels` channel owner reviews & public comments)
   is collected automatically via YouTubeCollector (`q040` - `q043`).
2. For PakWheels Forum threads or blog solutions you manually research:
   - Open `pakwheels_input.csv` and add curated rows (`thread_url`, `make`,
     `model`, `problem_title`, `problem_description`, `community_solution`, etc.).
   - Re-run `import_facebook_qa.bat` (or `auto_collect_bundle --skip-youtube`)
     to ingest them cleanly into `autocare.db` & `AI_Auto_Pakistan_Dataset/`.
