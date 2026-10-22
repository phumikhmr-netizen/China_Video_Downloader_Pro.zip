# China Video Downloader Pro (Android + Public Website)

## អ្វីដែលមាន
- Frontend responsive សម្រាប់ Android និង desktop
- FastAPI backend
- ពិនិត្យ metadata និងទាញយក content សាធារណៈតាម `yt-dlp`
- Allowlist សម្រាប់ Douyin, Kuaishou, Bilibili, Xiaohongshu និង link shortener ដែលពាក់ព័ន្ធ
- កំណត់ចំនួន request ក្នុងមួយនាទី និងទំហំឯកសារ
- មិនកំណត់ cookies, credentials, proxy ឬការរំលង anti-bot/DRM

## ដំណើរការក្នុងកុំព្យូទ័រ
ត្រូវការ Python 3.12 និង FFmpeg។
```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```
បើក `http://localhost:8000`។

## Deploy Public Website តាម Android ដោយ GitHub + Render
1. ទាញយក ZIP ហើយ extract វា។
2. បង្កើត repository ថ្មីនៅ https://github.com/new
3. Upload files ទាំងអស់ក្នុង ZIP ទៅ repository (Add file → Upload files → Commit changes)។
4. ចូល https://render.com ហើយ sign up / sign in។
5. ជ្រើស New → Blueprint ឬ New Web Service ភ្ជាប់ GitHub repository។
6. ប្រសិនបើប្រើ Blueprint វានឹងអាន `render.yaml`។ បើបង្កើត Web Service ដោយដៃ ជ្រើស Docker runtime។
7. ចុច Deploy ហើយរង់ចាំ Build/Deploy បញ្ចប់។
8. បើក URL `https://...onrender.com` ដែល Render ផ្ដល់ឱ្យ។
9. សាក `/api/health` ត្រូវបង្ហាញ `{"status":"ok","service":"China Video Downloader Pro"}`។

## ចំណាំសំខាន់
- Render plan, disk, runtime និង bandwidth អាចមានការផ្លាស់ប្តូរ។ ពិនិត្យតម្លៃ/លក្ខខណ្ឌបច្ចុប្បន្នមុន deploy។
- Public downloader មានហានិភ័យប្រើប្រាស់ខុស។ សម្រាប់ផលិតកម្ម គួរបន្ថែម authentication, queue, persistent rate limit, abuse monitoring, privacy policy និង terms of use។
- Rate limit ក្នុងគំរូនេះស្ថិតក្នុង memory ហើយអាច reset ពេល service restart; វាមិនមែនជាការការពារប្រឆាំង abuse កម្រិត production ទេ។
- វេទិកាអាចផ្លាស់ប្ដូររចនាសម្ព័ន្ធបាន ដូច្នេះ site មួយចំនួនអាចមិនដំណើរការគ្រប់ពេល។
- ប្រើសម្រាប់វីដេអូផ្ទាល់ខ្លួន ឬមានសិទ្ធិទាញយក។ កុំរំលង DRM, login, paywall ឬការការពាររបស់វេទិកា។
