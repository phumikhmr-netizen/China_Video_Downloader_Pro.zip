import os, re, time, tempfile, threading
from pathlib import Path
from urllib.parse import urlparse
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, HttpUrl
import yt_dlp

APP_DIR = Path(__file__).parent
ALLOWED_HOSTS = {
    "douyin.com", "www.douyin.com", "v.douyin.com",
    "kuaishou.com", "www.kuaishou.com", "v.kuaishou.com",
    "gifshow.com", "www.gifshow.com",
    "bilibili.com", "www.bilibili.com", "m.bilibili.com", "b23.tv",
    "xiaohongshu.com", "www.xiaohongshu.com", "xhslink.com",
    "www.xhslink.com",
}
MAX_DOWNLOAD_MB = int(os.getenv("MAX_DOWNLOAD_MB", "500"))
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "5"))
requests_by_ip = {}
rate_lock = threading.Lock()

app = FastAPI(title="China Video Downloader Pro", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")

class LinkRequest(BaseModel):
    url: HttpUrl

def validate_url(raw: str) -> str:
    parsed = urlparse(raw)
    if parsed.scheme != "https":
        raise HTTPException(400, "សូមប្រើ HTTPS link ដែលមានសុវត្ថិភាព។")
    host = (parsed.hostname or "").lower()
    if host not in ALLOWED_HOSTS:
        raise HTTPException(400, "វេទិកានេះមិនទាន់គាំទ្រ link នេះទេ។")
    if parsed.username or parsed.password:
        raise HTTPException(400, "Link នេះមិនត្រូវបានអនុញ្ញាតទេ។")
    return raw

def rate_check(request: Request):
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    with rate_lock:
        recent = [t for t in requests_by_ip.get(ip, []) if now - t < 60]
        if len(recent) >= RATE_LIMIT_PER_MINUTE:
            raise HTTPException(429, "សំណើច្រើនពេក។ សូមរង់ចាំមួយនាទី ហើយសាកម្ដងទៀត។")
        recent.append(now)
        requests_by_ip[ip] = recent

def ydl_options():
    return {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "format": "best[ext=mp4]/best",
        "merge_output_format": "mp4",
        "max_filesize": MAX_DOWNLOAD_MB * 1024 * 1024,
        "socket_timeout": 20,
        "retries": 1,
        "fragment_retries": 1,
        "restrictfilenames": True,
        # No cookies, credentials, proxy, or anti-bot bypass are configured.
    }

@app.get("/", response_class=HTMLResponse)
def home():
    return (APP_DIR / "static" / "index.html").read_text(encoding="utf-8")

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "China Video Downloader Pro"}

@app.post("/api/info")
def info(payload: LinkRequest, request: Request):
    rate_check(request)
    url = validate_url(str(payload.url))
    opts = ydl_options()
    opts["skip_download"] = True
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            data = ydl.extract_info(url, download=False)
        if not data:
            raise ValueError("No metadata")
        return {
            "title": data.get("title") or "Video",
            "duration": data.get("duration"),
            "uploader": data.get("uploader") or data.get("channel") or "",
            "platform": data.get("extractor_key") or "",
            "thumbnail": data.get("thumbnail") or "",
            "formats_available": bool(data.get("formats")),
            "note": "Only publicly accessible content is supported."
        }
    except Exception:
        raise HTTPException(422, "មិនអាចអានវីដេអូនេះបានទេ។ វាអាចជា private, ត្រូវការ login, មិនគាំទ្រ ឬត្រូវបានវេទិការារាំង។ សូមប្រើ download ផ្លូវការរបស់វេទិកា។")

@app.post("/api/download")
def download(payload: LinkRequest, request: Request):
    rate_check(request)
    url = validate_url(str(payload.url))
    tempdir = tempfile.mkdtemp(prefix="cvdp_")
    output_template = str(Path(tempdir) / "%(title).100B_%(id)s.%(ext)s")
    opts = ydl_options()
    opts.update({"outtmpl": output_template, "format": "best[ext=mp4]/best"})
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info_data = ydl.extract_info(url, download=True)
            filename = Path(ydl.prepare_filename(info_data))
            if not filename.exists():
                candidates = list(Path(tempdir).glob("*"))
                candidates = [p for p in candidates if p.is_file() and p.suffix.lower() in {".mp4", ".mkv", ".webm", ".mov"}]
                if not candidates:
                    raise ValueError("Output file missing")
                filename = candidates[0]
            if filename.stat().st_size > MAX_DOWNLOAD_MB * 1024 * 1024:
                raise HTTPException(413, f"វីដេអូលើសកម្រិត {MAX_DOWNLOAD_MB} MB។")
            return FileResponse(
                path=str(filename),
                filename=filename.name,
                media_type="application/octet-stream",
                background=None
            )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(422, "ទាញយកមិនបាន។ Link អាចជា private, ត្រូវការ login, មិនគាំទ្រ ឬត្រូវបានវេទិការារាំង។ សូមប្រើជម្រើសផ្លូវការរបស់វេទិកា។")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
