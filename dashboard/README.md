# Institutional Market Intelligence Dashboard

This folder contains the static presentation dashboard for the **Inteligencia financiera del mercado bursátil** project.

## Run locally

From the repository root:

```bash
python -m http.server 8000 -d dashboard
```

Then open `http://localhost:8000`.

## Design

The interface follows the project's institutional dark-terminal design system: dense analytical layout, Geist for narrative text, JetBrains Mono for quantitative output, semantic emerald/cyan/coral signals, thin borders, compact controls, and minimal roundedness.

## Data

Values shown in the dashboard come from the project's RQ1–RQ5 notebooks and executive report. The dashboard is a presentation layer; the analytical source of truth remains the notebooks, SQL layer, tests, and generated result files.

Historical results are not investment advice.
