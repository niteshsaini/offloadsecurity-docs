# Hosting the Offload Security documentation

This is a **standalone** [Docusaurus](https://docusaurus.io) site (the docs are the
repo root) extracted from the application monorepo so it can be hosted separately.

- Source of every page: `docs/` (sidebar auto-generated from the folder structure)
- Site config: `docusaurus.config.ts` (`url`, `baseUrl`), `sidebars.ts`
- Static assets / screenshots: `static/` (`static/img/screenshots/…`)
- Container hosting: `Dockerfile` + `nginx.conf` (+ `.dockerignore`)
- Build output (generated, git-ignored): `build/`

`build/`, `node_modules/`, and `.docusaurus/` are intentionally **not** committed
(see `.gitignore`) — they're produced by `npm run build`.

---

## Step 1 — Push this bundle to a new repository

From inside this folder:

```bash
git init
git add .
git commit -m "Initial import: Offload Security documentation site"

# create an EMPTY repo on your host first (no README/license), then:
git branch -M main
git remote add origin git@github.com:<org>/offload-security-docs.git   # or your GitLab/Bitbucket URL
git push -u origin main
```

Nothing here references the application code, so it's fully self-contained.

---

## Step 2 — Set your domain in the config

`docusaurus.config.ts` currently has:

```ts
url: 'https://docs.offloadsecurity.com',
baseUrl: '/',
```

- If you'll serve at **`docs.offloadsecurity.com`**, leave it as-is.
- If you'll serve at a **different** domain (e.g. an internal one), set `url` to that
  origin. `baseUrl` stays `/` when the site is at the domain root; use `/docs/` only
  if you serve it under a sub-path.
- `static/CNAME` is **only** read by GitHub Pages. For Docker/nginx hosting it's an
  inert file — delete it if you're not using GitHub Pages, or set it to your domain
  if you are.

---

## Step 3 — Self-host with Docker (recommended)

The included `Dockerfile` is a 2-stage build: Node builds the static site, then
**nginx** (`nginx.conf`) serves it on port **80** inside the container.

### Build & run

```bash
# Build the image (build context is the repo root)
docker build -t offload-docs .

# Run it — host port 4000 -> container port 80
docker run -d --name offload-docs --restart unless-stopped -p 4000:80 offload-docs

# Verify
curl -I http://localhost:4000/         # 200 OK
curl    http://localhost:4000/health   # "healthy"
```

Open `http://<host>:4000/` to confirm the site renders.

### Or with docker-compose

Drop this `docker-compose.yml` in the repo (or merge into an existing one):

```yaml
services:
  docs:
    build: .
    image: offload-docs
    container_name: offload-docs
    restart: unless-stopped
    ports:
      - "4000:80"          # host:container — change 4000 as needed
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/"]
      interval: 30s
      timeout: 5s
      retries: 3
```

```bash
docker compose up -d --build
```

### Put it behind a domain with HTTPS

The container speaks plain HTTP on 4000. Terminate TLS at a reverse proxy in front
of it (do **not** expose 4000 publicly). Two common options:

**Caddy (simplest — automatic Let's Encrypt):** `/etc/caddy/Caddyfile`
```
docs.offloadsecurity.com {
    reverse_proxy localhost:4000
}
```
`sudo systemctl reload caddy` — Caddy fetches/renews the cert automatically.

**nginx + certbot:** add a server block, then issue the cert:
```nginx
server {
    listen 80;
    server_name docs.offloadsecurity.com;
    location / { proxy_pass http://127.0.0.1:4000; proxy_set_header Host $host; }
}
```
```bash
sudo certbot --nginx -d docs.offloadsecurity.com   # adds the 443 block + auto-renew
```

If this box already runs the app behind a reverse proxy, just add the docs as
another `server_name` / virtual host pointing at `localhost:4000`.

### DNS

Point an `A`/`AAAA` record for your docs hostname at this server's public IP (or a
`CNAME` to its hostname). Wait for propagation, then load `https://<your-domain>/`.

### Updating the docs

```bash
git pull
docker compose up -d --build      # or: docker build -t offload-docs . && docker restart offload-docs
```

(If you set up CI on the new repo, have it rebuild + redeploy on push to `main`.)

---

## Alternatives (no server to run)

- **GitHub Pages:** `url` + `static/CNAME` are already set for `docs.offloadsecurity.com`.
  Add a workflow (or `npm run deploy` with `GIT_USER`/`USE_SSH`), enable
  **Settings → Pages → Source: GitHub Actions**, and point DNS `docs` →
  `<owner>.github.io`.
- **Netlify:** `netlify.toml` is preconfigured (base `.`, publish `build`, Node 20) —
  "Add new site → Import from Git", then set the custom domain.

---

## Local preview (sanity check before deploying)

```bash
npm ci
npm run build && npm run serve   # serves the production build at http://localhost:3000
```

See [PUBLISHING.md](PUBLISHING.md) for content structure, the sidebar, and how
screenshots are managed.
