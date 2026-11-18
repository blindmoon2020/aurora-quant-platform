const express = require('express');
const crypto = require('crypto');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// شبیه‌سازی Secure Vault (رمزنگاری AES-256 سازمانی مطابق استاندارد Addepar)
const ENCRYPTION_KEY = crypto.randomBytes(32); // در محیط واقعی از سرور متمرکز امن خوانده می‌شود
const IV_LENGTH = 16;

function encryptVaultData(text) {
    let iv = crypto.randomBytes(IV_LENGTH);
    let cipher = crypto.createCipheriv('aes-256-cbc', Buffer.from(ENCRYPTION_KEY), iv);
    let encrypted = cipher.update(text);
    encrypted = Buffer.concat([encrypted, cipher.final()]);
    return iv.toString('hex') + ':' + encrypted.toString('hex');
}

// دیتابیس ایمن موقت حافظه هسته (در سطح سرور)
let coreMemoryVault = {
    authVerified: false,
    userProfile: "Pending KYC",
    activeAAV: 50000,
    portfolio: [
        { symbol: 'XAUUSD', exchange: 'COMEX', current: 25, target: 30, basePrice: 2045.50 },
        { symbol: 'BRENT', exchange: 'ICE', current: 20, target: 20, basePrice: 82.10 },
        { symbol: 'WHEAT', exchange: 'CBOT', current: 15, target: 20, basePrice: 654.20 }
    ]
};

// API: تایید تست روانشناسی و گشایش پایانه امن
app.post('/api/auth/verify-psych', (req, res) => {
    const { riskScore } = req.body;
    coreMemoryVault.authVerified = true;
    coreMemoryVault.userProfile = riskScore === '1' ? "Ultra-Conservative" : "Institutional Balanced";
    
    res.json({
        success: true,
        message: "Institutional Vault Unlocked",
        encryptedToken: encryptVaultData(JSON.stringify(coreMemoryVault))
    });
});

// API: دریافت داده‌های سبد از سرور (جلوگیری از دستکاری کلاینت)
app.get('/api/portfolio/data', (req, res) => {
    if (!coreMemoryVault.authVerified) {
        return res.status(403).json({ error: "Access Denied: Zero-Trust Security Policy Enforced" });
    }
    res.json(coreMemoryVault);
});

// API: اعمال سرمایه جدید (AAV) در سرور
app.post('/api/portfolio/update-capital', (req, res) => {
    const { newAAV } = req.body;
    if (newAAV && !isNaN(newAAV)) {
        coreMemoryVault.activeAAV = parseFloat(newAAV);
        res.json({ success: true, activeAAV: coreMemoryVault.activeAAV });
    } else {
        res.status(400).json({ error: "Invalid Capital Value" });
    }
});

app.listen(PORT, () => {
    console.log(`[AURORA ENTERPRISE CORE] Secure server running on port ${PORT}`);
});
