# dvc-fixture

Mainly provides test fixture for e2e tests for GS Domain Validation process via HTTP and DNS.

Needs to run as a real domain, accepting DVC strings from e2e tests and making them available for domain validation checks — either as an HTTP file or as DNS TXT records via Cloudflare.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/dvc/http` | Stage a DVC for HTTP validation |
| POST | `/dvc/dns` | Stage a DVC as a DNS TXT record (blocks until created) |
| GET | `/.well-known/pki-validation/gsdv.txt` | Serves all staged HTTP DVCs |

POST body: `{"dvc": "your-validation-code"}`

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CLOUDFLARE_API_TOKEN` | yes | | Cloudflare API token |
| `CLOUDFLARE_ZONE_ID` | yes | | Cloudflare zone ID |
| `DNS_RECORD_NAME` | yes | | DNS name for TXT entries |
| `DNS_MAX_RECORDS` | no | `100` | Max TXT records before oldest are trimmed |
| `HTTP_QUEUE_SIZE` | no | `100` | Max DVCs kept in the HTTP file |
| `WELL_KNOWN_PATH` | no | `/.well-known/pki-validation/gsdv.txt` | Path for the HTTP validation file |

## Running

```bash
docker build -t dvc-fixture .
docker run -p 8000:8000 \
  -e CLOUDFLARE_API_TOKEN=your-token \
  -e CLOUDFLARE_ZONE_ID=your-zone-id \
  -e DNS_RECORD_NAME=example.com \
  dvc-fixture
```
