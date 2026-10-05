# Socio-Economic & Demographic Analysis of Indian Festivals

DAV team project by Jainam Jain (23108B0084), Vrushan Patil, Dhanush Chowke, Aditya Tambe and Vivek Jaiswal, B.E. Sem VII ECS, VIT. The brief is in `project details.PDF`.

## Deliverables map

| Task | Deliverable | Where |
|---|---|---|
| 1 Data | Raw data with source columns | `data/raw/rbi_holiday_matrix_raw.csv`, `economic_footfall_raw.csv` / `.json`, `festival_wikipedia_attribution.csv`, `census/C01_India_2011.xls`, `census/C01_AndhraPradesh_2011.xls`, `home_region_prior.csv`, `rbi_html/` (60 archived pages, 2022-2026) |
| 1 Data | Clean, analysis-ready tables | `data/processed/festival_observations.csv`, `festival_master.csv`, `state_profile.csv`, `economic_footfall_clean.csv`, `attribution_propensity.csv` (audit trail) |
| 1 Data | Data dictionary | `data/data_dictionary.md` / `.csv` |
| 2 ML | Pipeline code | `code/06_ml_models.py` |
| 2 ML | Model weights | `outputs/models/*.joblib` |
| 2 ML | Metrics and evaluation | `outputs/ml/*.csv`, `ml_summary.json`, figures `M01`–`M04` |
| 3 Stats | EDA report | `outputs/stats/statistical_summary.md` |
| 3 Stats | Validation tables | `T1`–`T10` CSVs |
| 3 Stats | Figures | `F01`–`F10` |
| 4 Blog | Article | `blog/blog_post.md` (source) and `blog_post.html` (paste-ready) |
| 4 Blog | Charts | high-res PNGs in `blog/images/`; interactive versions in `blog/interactive/` |
| 4 Blog | Engagement audit | `blog/engagement/` |
| 5 Video | Synthesis video | `video/Indian_Festivals_Project_Report.mp4` (1080p, about 5.4 min) |
| 5 Video | Script and slides | `narration_script.md`, `slides/` |
| All | Project report | `report/DAV Project Report_23108B0084.pdf` / `.docx` |

## Reproduce

Install dependencies, then run the scripts in order from the `code/` folder:

```bash
pip install -r requirements.txt
```

```bash
python 01_scrape_rbi_holidays.py && python 02_verify_wikipedia.py && python 03_economic_footfall_records.py && python 04_build_clean_dataset.py && python 05_eda_statistics.py && python 06_ml_models.py && python 07_data_dictionary.py && python 08_interactive_charts.py && python 09_blog_and_engagement.py && python 10_make_video.py && python 11_build_report.py && python 12_status_report.py
```

Notes:
- Script 10 needs `ffmpeg`, MS Edge (for Playwright) and an internet connection: the Indian English narration uses Microsoft's online voice through `edge-tts`.
- The study period is set once in `code/project_config.py`.
- Script 11 needs Microsoft Word to export the PDF.

## Remaining steps (author only)

Task 4 requires a real public post and genuine engagement. No code can or should do this for you.

1. **Publish the article.** Open `blog/blog_post.html` in a browser, copy everything, and paste it into a LinkedIn Article or Medium story. Images come across with the paste. If any image drops, re-add it from `blog/images/`. Optionally link the interactive charts after hosting them (for example on GitHub Pages).
2. **Record the post details.** Save the live URL in `blog/engagement/post_meta.json`:
   `{"live_url": "https://...", "published_on": "YYYY-MM-DD"}`
3. **Share it outside VIT.** Post it to your wider network and to relevant groups (data, India culture, economics). Reply to every comment.
4. **Log the engagement.** Add one row per external reaction or comment to `blog/engagement/engagement_log.csv`:
   - Set `is_same_institution` to `no` for people outside VIT.
   - Set `author_replied` to `yes` once you have answered.
   - Save a screenshot for each row in `screenshots/`.
5. **Regenerate the outputs.** Run these three scripts again:
   - `python 09_blog_and_engagement.py` rebuilds the audit report.
   - `python 10_make_video.py` rebuilds the video, whose reception slide updates automatically.
   - `python 11_build_report.py` rebuilds the report PDF.

## Data integrity statement

The dataset contains no synthetic data. Every record traces to one of:
- the RBI holiday matrix, 2022-2026;
- the Census of India 2011 (Table C-01, India and Andhra Pradesh district tables);
- the DoPT list of compulsory Central Government holidays (O.M. F.No.12/2/2023-JCA, 3 July 2025);
- a Wikipedia infobox or a Government page, used to label each festival's tradition and home community;
- one of 78 economic figures, each confirmed on its source page on 28 Sep 2026.

Figures that appeared only in search snippets were excluded (for example, Diwali trade for 2022).

## How under-counting is avoided

So that no tradition, state or festival is under-represented by an accident of the calendar:

- **Sunday correction.** RBI lists no Sunday dates, so a festival on a Sunday disappears for that year. Each festival is averaged only over the years it could be listed.
- **Shared dates.** RBI prints one combined label per date. A festival that a state is confirmed to observe counts in full there, even on a shared date. Confirmation comes from RBI itself (a date where the festival stood alone), the DoPT compulsory list, or the festival's home community.
- **What stays uncertain** is split by an evidence score and flagged (19 of 101 festivals).

Not covered: festivals with no bank holiday, restricted and district-level holidays, and union territories without an RBI office. Full details are in `data/data_dictionary.md`.

## Privacy note

The filled engagement log and screenshots are not in this public repository. They name people outside the team and are kept for the course submission only.
