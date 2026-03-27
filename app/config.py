from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    cloudflare_api_token: str
    cloudflare_zone_id: str
    dns_record_name: str
    dns_max_records: int = 40
    dns_max_age_hours: int = 24
    http_queue_size: int = 100
    well_known_path: str = "/.well-known/pki-validation/gsdv.txt"
