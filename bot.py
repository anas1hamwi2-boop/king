import os
import requests
from flask import Flask, request, jsonify, render_template_string

API_TARGET = os.environ.get('API_TARGET', 'http://85.215.137.163:9393')
API_KEY = os.environ.get('API_KEY', 'hanenbano')
HOST = '0.0.0.0'
PORT = int(os.environ.get('PORT', 5000))

app = Flask(__name__)

SITE_HTML = r'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Social Info | Al King</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css"
          integrity="sha512-DTOQO9RWCH3ppGqcWaEA1BIZOC6xxalwEsw9c2QQeAIftl+Vegovlnee1c9QX4TctnWMn13TZye+giMm8e2LwA=="
          crossorigin="anonymous" referrerpolicy="no-referrer" />
    <style>
        :root {
            --bg: #02000f;
            --card-bg: rgba(10, 10, 35, 0.5);
            --primary: #00e0ff;
            --secondary: #d400ff;
            --accent: #ffcc00;
            --text: #f0f0f0;
            --glass-border: rgba(255, 255, 255, 0.08);
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', 'Tajawal', sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            display: flex; align-items: center; justify-content: center;
            overflow-x: hidden; position: relative;
        }
        .loader-overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: #02000f; display: flex; flex-direction: column; align-items: center; justify-content: center;
            z-index: 9999; transition: opacity 0.5s ease, visibility 0.5s;
        }
        .loader-overlay.hidden { opacity: 0; visibility: hidden; }
        .loader-title {
            font-size: 2.8rem; font-weight: 900; letter-spacing: 3px;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 2rem; filter: drop-shadow(0 0 20px var(--primary));
        }
        .loader-bar-container { width: 220px; height: 3px; background: rgba(255,255,255,0.1); border-radius: 20px; overflow: hidden; }
        .loader-bar { width: 0%; height: 100%; background: linear-gradient(90deg, var(--primary), var(--secondary)); border-radius: 20px; animation: loaderProgress 1.8s ease-in-out forwards; box-shadow: 0 0 25px var(--primary); }
        @keyframes loaderProgress { 0%{width:0%} 100%{width:100%} }
        .search-loader-overlay {
            position: fixed; top:0; left:0; width:100%; height:100%;
            background: rgba(2,0,15,0.9); backdrop-filter: blur(10px);
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            z-index: 9998; transition: opacity 0.4s, visibility 0.4s;
        }
        .search-loader-overlay.hidden { opacity: 0; visibility: hidden; }
        .search-loader-text {
            font-size: 1.8rem; font-weight: 700; color: var(--primary);
            margin-bottom: 2rem; text-shadow: 0 0 20px var(--primary);
            animation: pulseText 1.5s infinite;
        }
        @keyframes pulseText { 0%,100%{opacity:1} 50%{opacity:0.5} }
        .search-spinner {
            width: 55px; height: 55px; border:4px solid rgba(255,255,255,0.08);
            border-top:4px solid var(--primary); border-radius: 50%;
            animation: spin 0.8s linear infinite; box-shadow: 0 0 35px var(--primary);
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        canvas#particles { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; pointer-events: none; }
        .main-container { position: relative; z-index: 2; width: 95%; max-width: 700px; display: flex; flex-direction: column; gap: 1.8rem; }
        .main-view { transition: opacity 0.3s, transform 0.3s; }
        .main-view.hidden { display: none; }
        .hero { text-align: center; animation: floatHero 6s infinite ease-in-out; }
        @keyframes floatHero { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-10px)} }
        .glitch-title {
            font-size: 3.5rem; font-weight: 900; letter-spacing: 5px;
            background: linear-gradient(90deg, var(--primary), var(--secondary), var(--primary));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
            filter: drop-shadow(0 0 30px rgba(0,240,255,0.8)); animation: glitch 2.5s infinite;
        }
        @keyframes glitch {
            0%,100%{text-shadow:3px 3px var(--primary),-3px -3px var(--secondary)}
            25%{text-shadow:-3px 3px var(--secondary),3px -3px var(--primary)}
            50%{text-shadow:2px -2px var(--primary),-2px 2px var(--secondary)}
            75%{text-shadow:-2px -2px var(--secondary),2px 2px var(--primary)}
        }
        .platforms-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(130px,1fr)); gap: 14px;
            backdrop-filter: blur(20px); background: var(--card-bg); padding: 1.8rem; border-radius: 40px;
            border:1px solid var(--glass-border); box-shadow: 0 30px 60px rgba(0,0,0,0.7), inset 0 0 30px rgba(0,240,255,0.05);
        }
        .platform-card {
            background: rgba(25,25,55,0.45); backdrop-filter: blur(15px);
            border:1px solid rgba(255,255,255,0.1); border-radius: 28px; padding: 1.3rem 0.8rem;
            cursor: pointer; transition: all 0.4s cubic-bezier(0.175,0.885,0.32,1.275);
            text-align: center; position: relative; overflow: hidden;
        }
        .platform-card::before {
            content: ''; position: absolute; top:-50%; left:-50%; width:200%; height:200%;
            background: radial-gradient(circle at center, rgba(255,255,255,0.1) 0%, transparent 70%);
            opacity: 0; transition: opacity 0.3s;
        }
        .platform-card:hover::before { opacity: 1; }
        .platform-card.active {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            transform: scale(1.05); border-color: transparent; box-shadow: 0 0 40px rgba(0,240,255,0.8);
        }
        .platform-card i { font-size: 2.3rem; margin-bottom: 0.4rem; filter: drop-shadow(0 0 15px rgba(0,240,255,0.6)); transition: transform 0.3s; }
        .platform-card:hover i { transform: rotateY(360deg); }
        .platform-card span { display: block; font-weight: 700; font-size: 0.95rem; letter-spacing: 0.5px; }
        .search-section {
            backdrop-filter: blur(20px); background: var(--card-bg); border-radius: 40px; padding: 1.5rem;
            border:1px solid var(--glass-border); box-shadow: 0 30px 60px rgba(0,0,0,0.7);
            display: flex; flex-wrap: wrap; gap: 12px; align-items: center;
        }
        .input-wrapper { flex:1; position: relative; min-width: 200px; }
        .input-wrapper i { position: absolute; left: 18px; top: 50%; transform: translateY(-50%); color: var(--primary); font-size: 1.3rem; }
        #searchInput {
            width: 100%; padding: 16px 22px 16px 54px; border:2px solid rgba(255,255,255,0.12);
            border-radius: 30px; background: rgba(20,20,45,0.6); color: #fff; font-size: 1.1rem;
            outline: none; backdrop-filter: blur(10px); transition: 0.3s;
        }
        #searchInput:focus { border-color: var(--primary); box-shadow: 0 0 35px rgba(0,240,255,0.4); }
        .action-btns { display: flex; gap: 8px; }
        #searchBtn, #pasteBtn {
            background: linear-gradient(135deg, var(--primary), var(--secondary)); border: none;
            border-radius: 30px; padding: 14px 20px; font-size: 1.2rem; font-weight: bold; color: #000;
            cursor: pointer; box-shadow: 0 0 30px rgba(0,240,255,0.5); transition: all 0.3s;
            display: flex; align-items: center; gap: 8px; white-space: nowrap;
        }
        #pasteBtn { background: linear-gradient(135deg, var(--accent), #ff8800); }
        #searchBtn:hover, #pasteBtn:hover { transform: translateY(-3px); box-shadow: 0 0 60px rgba(255,0,200,0.9); }
        .error-msg {
            background: rgba(255,0,60,0.12); border-left:5px solid #ff0040; padding: 14px 20px;
            border-radius: 20px; color: #ff6b81; display: none; backdrop-filter: blur(15px);
            font-weight: 500; text-align: center; transition: opacity 0.3s;
        }
        .result-view {
            display: none; backdrop-filter: blur(25px); background: var(--card-bg);
            border-radius: 40px; padding: 2rem; border:1px solid var(--glass-border);
            box-shadow: 0 40px 80px rgba(0,0,0,0.8);
            animation: resultAppear 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
        }
        @keyframes resultAppear {
            from { opacity: 0; transform: scale(0.9) translateY(20px); }
            to { opacity: 1; transform: scale(1) translateY(0); }
        }
        .back-btn {
            position: absolute; top: 20px; left: 20px;
            background: rgba(255,255,255,0.1); border:1px solid var(--primary);
            color: var(--primary); width: 40px; height: 40px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            cursor: pointer; transition: all 0.3s; font-size: 1.2rem;
        }
        .back-btn:hover { background: var(--primary); color: #000; box-shadow: 0 0 25px var(--primary); }
        .profile-header { text-align: center; margin-bottom: 1.5rem; }
        .avatar {
            width: 110px; height: 110px; border-radius: 50%; object-fit: cover;
            border:3px solid transparent; background: linear-gradient(45deg, var(--primary), var(--secondary)) border-box;
            -webkit-mask: radial-gradient(circle, white 58%, transparent 59%);
            mask: radial-gradient(circle, white 58%, transparent 59%);
            box-shadow: 0 0 60px rgba(0,240,255,0.7), 0 0 100px rgba(200,0,255,0.5);
            animation: glowPulse 3s infinite alternate;
        }
        @keyframes glowPulse {
            from { box-shadow:0 0 40px var(--primary),0 0 80px var(--secondary); }
            to { box-shadow:0 0 80px var(--secondary),0 0 120px var(--primary); }
        }
        .username {
            font-size: 2.2rem; font-weight: 800;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-top:0.6rem;
        }
        .fullname { color: #c0c0c0; font-size: 1.1rem; margin-bottom: 1.2rem; }
        .details-table {
            margin-top: 1rem; background: rgba(255,255,255,0.03); border-radius: 20px;
            padding: 14px; backdrop-filter: blur(10px);
        }
        .detail-row {
            display: flex; justify-content: space-between; padding: 8px 0;
            border-bottom:1px solid rgba(255,255,255,0.06);
        }
        .detail-key { color: var(--accent); font-weight: 600; }
        .detail-value { color: #ddd; word-break: break-word; }
        .action-row { display: flex; justify-content: center; gap: 12px; margin-top: 1.5rem; }
        .copy-btn {
            background: rgba(255,255,255,0.1); border:1px solid var(--primary); color: var(--primary);
            padding: 10px 24px; border-radius: 30px; cursor: pointer; font-weight: bold; transition: all 0.3s;
        }
        .copy-btn:hover { background: var(--primary); color: #000; }
        .developer-tag { margin-top: 1.5rem; text-align: center; color: var(--accent); font-weight: 700; letter-spacing: 1px; }
    </style>
</head>
<body>
<div class="loader-overlay" id="loaderOverlay">
    <div class="loader-title">Social Info</div>
    <div class="loader-bar-container"><div class="loader-bar"></div></div>
</div>
<div class="search-loader-overlay hidden" id="searchLoader">
    <div class="search-loader-text">جاري جلب المعلومات...</div>
    <div class="search-spinner"></div>
</div>
<canvas id="particles"></canvas>
<div class="main-container">
    <div class="main-view" id="mainView">
        <div class="hero"><h1 class="glitch-title">Social Info</h1></div>
        <div class="platforms-grid" id="platformGrid"></div>
        <div class="search-section">
            <div class="input-wrapper">
                <i class="fas fa-search"></i>
                <input type="text" id="searchInput" placeholder="أدخل المعرف..." autocomplete="off" autofocus>
            </div>
            <div class="action-btns">
                <button id="pasteBtn"><i class="fas fa-paste"></i> لصق</button>
                <button id="searchBtn"><i class="fas fa-magic"></i> كشف</button>
            </div>
        </div>
        <div class="error-msg" id="errorMsg"></div>
    </div>
    <div class="result-view" id="resultView">
        <div class="back-btn" id="backBtn"><i class="fas fa-arrow-right"></i></div>
        <div class="profile-header">
            <img id="avatarImg" class="avatar" src="" alt="avatar">
            <div class="username" id="usernameDisplay"></div>
            <div class="fullname" id="fullnameDisplay"></div>
        </div>
        <div class="details-table" id="detailsTable"></div>
        <div class="action-row">
            <button class="copy-btn" id="copyBtn"><i class="fas fa-copy"></i> نسخ المعلومات</button>
        </div>
        <div class="developer-tag">👨‍💻 Developer: @k8_0c</div>
    </div>
</div>

<script>
    const API_KEY = '{{ API_KEY }}';
    const IMG_PROXY = '/img?url=';

    const platforms = [
        { id: 'instagram', icon: 'fab fa-instagram', name: 'إنستغرام' },
        { id: 'tiktok', icon: 'fab fa-tiktok', name: 'تيك توك' },
        { id: 'twitter', icon: 'fab fa-x-twitter', name: 'تويتر' },
        { id: 'youtube', icon: 'fab fa-youtube', name: 'يوتيوب' },
        { id: 'telegram', icon: 'fab fa-telegram-plane', name: 'تلغرام' },
        { id: 'facebook', icon: 'fab fa-facebook', name: 'فيسبوك' }
    ];

    let currentPlatform = 'instagram';
    let currentData = null;

    const mainView = document.getElementById('mainView');
    const resultView = document.getElementById('resultView');
    const backBtn = document.getElementById('backBtn');
    const platformGrid = document.getElementById('platformGrid');
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const pasteBtn = document.getElementById('pasteBtn');
    const errorMsg = document.getElementById('errorMsg');
    const searchLoader = document.getElementById('searchLoader');
    const avatarImg = document.getElementById('avatarImg');
    const usernameDisplay = document.getElementById('usernameDisplay');
    const fullnameDisplay = document.getElementById('fullnameDisplay');
    const detailsTable = document.getElementById('detailsTable');
    const copyBtn = document.getElementById('copyBtn');

    platforms.forEach(p => {
        const card = document.createElement('div');
        card.className = 'platform-card';
        card.dataset.platform = p.id;
        card.innerHTML = `<i class="${p.icon}"></i><span>${p.name}</span>`;
        if (p.id === currentPlatform) card.classList.add('active');
        card.addEventListener('click', () => selectPlatform(p.id));
        platformGrid.appendChild(card);
    });

    function selectPlatform(platformId) {
        currentPlatform = platformId;
        document.querySelectorAll('.platform-card').forEach(c => c.classList.remove('active'));
        const activeCard = document.querySelector(`.platform-card[data-platform="${platformId}"]`);
        if (activeCard) activeCard.classList.add('active');
    }

    function showError(text) {
        errorMsg.textContent = '❌ ' + text;
        errorMsg.style.display = 'block';
    }

    function displayProfile(data) {
        currentData = data.data;
        const d = currentData;
        let avatarUrl = d.profile_pic_url || d.profile_picture || d.profile_image || d.profile_pic || '';
        avatarImg.src = avatarUrl ? IMG_PROXY + encodeURIComponent(avatarUrl) : '';
        usernameDisplay.textContent = d.username || d.name || d.channel_name || d.number || '';
        fullnameDisplay.textContent = d.full_name || d.nickname || d.name || d.channel_name || '';

        detailsTable.innerHTML = '';
        const ignoredKeys = ['profile_pic_url','profile_picture','profile_image','profile_pic'];
        const keyNames = {
            user_id: '🆔 معرف المستخدم',
            username: '👤 اسم المستخدم',
            full_name: '📛 الاسم الكامل',
            name: '📛 الاسم',
            nickname: '📛 اللقب',
            bio: '📝 النبذة',
            description: '📝 الوصف',
            is_private: '🔒 حساب خاص',
            creation_year: '📅 سنة الإنشاء',
            create_date: '📅 تاريخ الإنشاء',
            language: '🌐 اللغة',
            country: '🌍 الدولة',
            provider: '🏢 المزود',
            valid: '✅ صالح',
            timezone: '🌐 المنطقة الزمنية',
            number: '📞 الرقم',
            location: '📍 الموقع',
            created_at: '📅 أنشئ في',
            followers: '👥 المتابعون',
            following: '👤 يتـابع',
            posts: '📸 المنشورات',
            likes: '❤️ الإعجابات',
            videos: '📹 الفيديوهات',
            subscribers: '👥 المشتركون',
            tweets: '🐦 التغريدات'
        };

        for (let [key, value] of Object.entries(d)) {
            if (ignoredKeys.includes(key) || value === null || value === undefined) continue;
            if (typeof value === 'object') {
                value = JSON.stringify(value);
            } else if (typeof value === 'number') {
                value = value.toLocaleString();
            } else {
                value = String(value);
            }
            const row = document.createElement('div');
            row.className = 'detail-row';
            const keySpan = document.createElement('span');
            keySpan.className = 'detail-key';
            keySpan.textContent = keyNames[key] || key;
            const valueSpan = document.createElement('span');
            valueSpan.className = 'detail-value';
            valueSpan.textContent = value;
            row.appendChild(keySpan);
            row.appendChild(valueSpan);
            detailsTable.appendChild(row);
        }

        mainView.classList.add('hidden');
        resultView.style.display = 'block';
        searchLoader.classList.add('hidden');
    }

    async function fetchProfile() {
        const identifier = searchInput.value.trim();
        if (!identifier) {
            showError('الرجاء إدخال معرف المستخدم');
            return;
        }
        errorMsg.style.display = 'none';
        searchLoader.classList.remove('hidden');
        mainView.classList.add('hidden');
        try {
            const url = `/${currentPlatform}/${encodeURIComponent(identifier)}?key=${API_KEY}`;
            const response = await fetch(url);
            const json = await response.json();
            if (!response.ok || json.status !== 'success') {
                throw new Error(json.message || 'الحساب غير موجود');
            }
            displayProfile(json);
        } catch (err) {
            searchLoader.classList.add('hidden');
            mainView.classList.remove('hidden');
            showError(err.message || 'فشل الاتصال بالخادم');
        }
    }

    backBtn.addEventListener('click', () => {
        resultView.style.display = 'none';
        mainView.classList.remove('hidden');
        searchLoader.classList.add('hidden');
        errorMsg.style.display = 'none';
        searchInput.value = '';
        searchInput.focus();
    });

    searchBtn.addEventListener('click', fetchProfile);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') fetchProfile();
    });

    pasteBtn.addEventListener('click', async () => {
        try {
            const clipText = await navigator.clipboard.readText();
            if (!clipText) return;
            const urlPatterns = [
                { regex: /(?:https?:\/\/)?(?:www\.)?instagram\.com\/([A-Za-z0-9_.]+)/, platform: 'instagram' },
                { regex: /(?:https?:\/\/)?(?:www\.)?tiktok\.com\/@([A-Za-z0-9_.]+)/, platform: 'tiktok' },
                { regex: /(?:https?:\/\/)?(?:www\.)?(?:twitter|x)\.com\/([A-Za-z0-9_]+)/, platform: 'twitter' },
                { regex: /(?:https?:\/\/)?(?:www\.)?youtube\.com\/@([A-Za-z0-9_.]+)/, platform: 'youtube' },
                { regex: /(?:https?:\/\/)?(?:www\.)?facebook\.com\/([A-Za-z0-9.]+)/, platform: 'facebook' },
                { regex: /(?:https?:\/\/)?t\.me\/([A-Za-z0-9_]+)/, platform: 'telegram' }
            ];
            for (let {regex, platform} of urlPatterns) {
                const match = clipText.match(regex);
                if (match) {
                    selectPlatform(platform);
                    searchInput.value = match[1];
                    fetchProfile();
                    return;
                }
            }
            searchInput.value = clipText.trim();
        } catch (err) {
            alert('لم يتمكن من قراءة الحافظة. الصق يدوياً.');
        }
    });

    copyBtn.addEventListener('click', () => {
        if (!currentData) return;
        const d = currentData;
        let lines = [];
        const platformName = platforms.find(p => p.id === currentPlatform)?.name || '';
        lines.push(`📌 ${platformName} User Info`);
        lines.push('━━━━━━━━━━━━━━━━━━━━━');
        if (d.username) lines.push(`👤 Username: @${d.username}`);
        if (d.full_name || d.name || d.nickname) lines.push(`📛 Name: ${d.full_name || d.name || d.nickname}`);
        if (d.user_id) lines.push(`🆔 User ID: ${d.user_id}`);
        if (d.bio || d.description) lines.push(`📝 Bio: ${d.bio || d.description}`);
        if (d.followers !== undefined) lines.push(`👥 Followers: ${d.followers.toLocaleString()}`);
        if (d.following !== undefined) lines.push(`👤 Following: ${d.following.toLocaleString()}`);
        if (d.posts !== undefined) lines.push(`📸 Posts: ${d.posts.toLocaleString()}`);
        if (d.likes !== undefined) lines.push(`❤️ Likes: ${d.likes.toLocaleString()}`);
        if (d.videos !== undefined) lines.push(`📹 Videos: ${d.videos.toLocaleString()}`);
        if (d.subscribers !== undefined) lines.push(`👥 Subscribers: ${d.subscribers}`);
        if (d.tweets !== undefined) lines.push(`📝 Tweets: ${d.tweets.toLocaleString()}`);
        if (d.is_private !== undefined) lines.push(`🔒 Private: ${d.is_private ? 'Yes' : 'No'}`);
        if (d.creation_year) lines.push(`📅 Creation Year: ${d.creation_year}`);
        if (d.country) lines.push(`🌍 Country: ${d.country}`);
        if (d.provider) lines.push(`🏢 Provider: ${d.provider}`);
        lines.push('━━━━━━━━━━━━━━━━━━━━━');
        lines.push('by: @k8_0c');
        const text = lines.join('\n');
        navigator.clipboard.writeText(text).then(() => {
            copyBtn.innerHTML = '<i class="fas fa-check"></i> تم النسخ';
            setTimeout(() => { copyBtn.innerHTML = '<i class="fas fa-copy"></i> نسخ المعلومات'; }, 2000);
        }).catch(() => alert('تعذر النسخ.'));
    });

    window.addEventListener('load', () => {
        setTimeout(() => {
            document.getElementById('loaderOverlay').classList.add('hidden');
        }, 200);
    });

    const canvas = document.getElementById('particles');
    const ctx = canvas.getContext('2d');
    let particles = [], maxParticles = 100, animFrame;
    function resize() { canvas.width = innerWidth; canvas.height = innerHeight; }
    window.addEventListener('resize', resize);
    resize();
    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.vx = (Math.random() - 0.5) * 0.8;
            this.vy = (Math.random() - 0.5) * 0.8;
            this.size = Math.random() * 2.5 + 1.2;
            this.opacity = Math.random() * 0.7 + 0.3;
            this.color = Math.random() < 0.5 ? '0, 240, 255' : '180, 0, 255';
        }
        update() {
            this.x += this.vx; this.y += this.vy;
            if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
            if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
        }
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, 2*Math.PI);
            ctx.fillStyle = `rgba(${this.color}, ${this.opacity})`;
            ctx.shadowBlur = 20;
            ctx.shadowColor = `rgba(${this.color}, 0.9)`;
            ctx.fill();
            ctx.shadowBlur = 0;
        }
    }
    function initParticles() { for (let i=0; i<maxParticles; i++) particles.push(new Particle()); }
    function animateParticles() {
        ctx.clearRect(0,0,canvas.width,canvas.height);
        particles.forEach(p => {
            p.update(); p.draw();
            for (let j=0; j<particles.length; j++) {
                const dx = p.x - particles[j].x, dy = p.y - particles[j].y, dist = Math.sqrt(dx*dx+dy*dy);
                if (dist < 130) {
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(255,255,255,${0.04*(1 - dist/130)})`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            }
        });
        animFrame = requestAnimationFrame(animateParticles);
    }
    initParticles(); animateParticles();
    window.addEventListener('beforeunload', () => cancelAnimationFrame(animFrame));
</script>
</body>
</html>'''


@app.route('/img')
def proxy_image():
    url = request.args.get('url')
    if not url:
        return "Missing URL", 400
    try:
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        return resp.content, 200, {'Content-Type': resp.headers.get('Content-Type', 'image/jpeg')}
    except:
        return "", 500

# ================== بروكسي API المحمي ==================
@app.route('/<platform>/<identifier>')
def proxy_api(platform, identifier):
    if platform == 'phone':
        return jsonify({"status": "error", "message": "غير مدعوم"}), 400

    key = request.args.get('key', '')
    if key != API_KEY:
        return jsonify({"status": "error", "message": "مفتاح API غير صالح"}), 403

    target_url = f"{API_TARGET}/{platform}/{identifier}"
    try:
        resp = requests.get(target_url, timeout=15)
        data = resp.json() if resp.headers.get('content-type','').startswith('application/json') else resp.text
        response = jsonify(data)
        response.status_code = resp.status_code
    except Exception as e:
        response = jsonify({"status":"error","message": f"فشل الاتصال: {str(e)}"})
        response.status_code = 500

    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/')
def home():
    rendered = SITE_HTML.replace('{{ API_KEY }}', API_KEY)
    return render_template_string(rendered)

if __name__ == '__main__':
    app.run(host=HOST, port=PORT)
