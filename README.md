# The Famous Few

Which of Britain and Ireland's 4,147 hillforts get online attention, and why?

**Interactive version:** https://tristan-hotham.github.io/famous-few/

This repository holds the interactive page, the site-level dataset, monthly pageview series and the analysis code for the study *The Famous Few: Size, Fame and Online Attention to 4,147 Hillforts in Britain and Ireland* by Tristan Hotham (Independent researcher, ORCID 0000-0003-4931-9349).

## Files

- `index.html`: the interactive page (map, charts, search).
- `data/hillforts_attention.csv`: one row per Atlas hillfort with Atlas variables (area, ramparts, scheduling, excavations, dating, reuse), name cues, access measures, matched Wikipedia articles (en, cy, ga, gd), pageviews 2016 to 2025, Wikimedia Commons category file counts and Wikidata details.
- `data/monthly_pageviews_en.csv`: monthly English Wikipedia human pageviews, January 2016 to December 2025, for every site with an English article.
- `code/`: Python scripts used to build features, match articles, run the models and build the page and paper.
- `figs/`: static figures.

## Sources and licence

- Site data: Lock, G. and Ralston, I. 2017. *Atlas of Hillforts of Britain and Ireland*. https://hillforts.arch.ox.ac.uk (CC BY-SA 4.0), via the Atlas source data released with Middleton, M. 2024, *The Hillforts Primer* (https://github.com/MikeDairsie/hillforts-primer).
- Pageviews: Wikimedia REST API (human user agents). Articles and identifiers: Wikidata (CC0) and Wikipedia.
- Towns and population: GeoNames (CC BY 4.0). Base map: Natural Earth.

Because the Atlas data are CC BY-SA 4.0, the derived dataset and this page are released under CC BY-SA 4.0. Code is MIT.

Google Maps review counts were not collected: Google's terms do not allow place content to be scraped or stored for analysis.
