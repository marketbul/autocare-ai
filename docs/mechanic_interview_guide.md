# Recording mechanic notes

Mechanic notes add practical workshop knowledge next to the owner's manual. Every
note is shown in answers as a source, e.g. *"Mechanic interview: M. Akram (20 yrs,
Toyota-authorised workshop, Lahore), 2026-10-20"*, so it must be real and traceable.

## Before the interview
- Explain the project and get **written consent** (proposal §9.2). Ask whether they
  want their **name** shown or a label such as "Mechanic A". Write `yes` in the
  `consent` column only when you have it in writing.
- Note their experience in years, the workshop type (authorised dealer, independent,
  specialist) and city.

## What to ask (per symptom)
Use the most common Corolla problems from your symptom list (brakes, overheating,
check-engine light, battery/starting, AC, suspension noise, gearbox).
1. When a customer says "<symptom>", what is the usual cause on a Corolla of these years?
2. What can the owner safely check themselves?
3. Is it safe to keep driving? When must they stop?
4. What does the repair normally involve, and what is often recommended unnecessarily?
5. Anything different for Pakistani conditions (heat, dust, fuel quality, CNG)?

## Writing a note
- One note = one topic, 1–4 sentences, in **English**, in the mechanic's meaning (not your opinion).
- Keep it factual and specific. No prices in notes (they go out of date); prices belong in the
  price table (M9, Tier 2).
- `manufacturer, model, years`: the cars the advice applies to, e.g. `Toyota, Corolla, 2014-2019`.
  Leave all three blank only for advice that applies to any car.
- Read the note back to the mechanic and correct it with them.

## Example row (illustrative format only; do NOT load invented advice)
| column | example |
|---|---|
| note_id | MN-001 |
| mechanic_name | Mechanic A |
| experience_years | 18 |
| workshop | Independent workshop |
| city | Lahore |
| interview_date | 2026-10-20 |
| consent | yes |
| manufacturer / model / years | Toyota / Corolla / 2014-2019 |
| topic | Grinding noise when braking |
| advice | *(the mechanic's actual words, summarised)* |

## Load
```
python -m ingest.mechanic_notes --csv data\mechanic_notes.csv
```
After editing the CSV, reload with `--replace` so old versions of notes are removed.
Answers will then list sources under **From your manual** and **From mechanics**.
If a note contradicts the manual, the system follows the manual.
