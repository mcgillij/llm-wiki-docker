# 3dSpace Wiki

Technical knowledge base for the [3dSpace](https://github.com/user/3d-space) Godot project. Served via MkDocs Material theme in Docker.

## Quick Start

```bash
cd ~/workspace/wiki
docker compose up          # foreground (Ctrl+C to stop)
docker compose up -d       # detached/background mode
```

Browse at **http://localhost:8080**

Stop the server:
```bash
docker compose down        # stops and removes container
# or just Ctrl+C if running in foreground
```

## Directory Structure

```
wiki/
├── docker-compose.yml     # Docker Compose config (port 8080)
├── Dockerfile             # Builds from squidfunk/mkdocs-material
├── mkdocs.yml             # MkDocs configuration & navigation
├── preprocess_wikilinks.py  # Converts [[wikilink]] → markdown links
├── content/               # Wiki pages (mounted as volume for hot-reload)
│   ├── index.md           # Home page
│   ├── log.md             # Edit history log
│   ├── SCHEMA.md          # Page schema conventions
│   ├── entities/          # Entity pages (autoloads, services)
│   └── concepts/          # Concept pages (systems, architecture)
└── README.md              # This file
```

## Workflow

### Adding a new wiki page

1. Create the markdown file in `content/entities/` or `content/concepts/`
2. Follow the [schema conventions](SCHEMA.md)
3. Run the preprocessor to convert wikilinks:
   ```bash
   python3 preprocess_wikilinks.py
   ```
4. Add an entry to `mkdocs.yml` under the appropriate nav section
5. The server auto-reloads — just refresh your browser

### Editing existing pages

1. Edit files directly in `content/` (hot-reload is automatic)
2. If you add new wikilinks, run:
   ```bash
   python3 preprocess_wikilinks.py
   ```
3. Refresh the browser

## Features

- **Dark mode** — auto-detects system preference, toggle in top-right corner
- **Search** — full-text search across all pages (top-right search bar)
- **Sidebar navigation** — hierarchical TOC with section grouping
- **Hot-reload** — edit markdown files and see changes instantly
- **Wikilinks** — `[[page-name]]` syntax auto-resolves to proper links

## Troubleshooting

### Port 8080 already in use
```bash
fuser -k 8080/tcp   # kill whatever's using the port
docker compose up    # restart
```

### Wikilinks not resolving
Run the preprocessor after adding new pages or wikilinks:
```bash
python3 preprocess_wikilinks.py
```

### Container won't start
Check for zombie containers:
```bash
docker ps -a --filter "publish=8080"   # list any stuck containers
docker rm -f <container_id>            # remove them
docker compose up                      # restart fresh
```
