# 🔐 Wallet Connection Troubleshooting Guide

## 🚨 **Common Issues & Solutions**

### **Issue 1: "Wallet Not Ready" Error**
**Problem:** Wallet extension not installed or locked

**Solution:**
1. **Install Wallet Extension:**
   - [Phantom Wallet](https://phantom.app/)
   - [Solflare Wallet](https://solflare.com/)
   - [Backpack Wallet](https://backpack.app/)

2. **Unlock Wallet:**
   - Click the wallet extension icon
   - Enter your password
   - Make sure it's unlocked before connecting

3. **Refresh Page:**
   - After installing/unlocking, refresh the browser page

---

### **Issue 2: "Failed to Connect" Error**
**Problem:** Network mismatch or RPC endpoint issues

**Solution:**
1. **Check Network Settings:**
   - Open your wallet extension
   - Ensure it's set to **Devnet** (for development)
   - Change from Mainnet → Devnet if needed

2. **Verify RPC Endpoint:**
   - Current config: `https://api.devnet.solana.com`
   - Should match your wallet's network setting

3. **Clear Browser Cache:**
   - Clear localStorage: `localStorage.clear()`
   - Refresh the page
   - Try connecting again

---

### **Issue 3: "Wallet Not Detected"**
**Problem:** Wallet adapter not recognizing installed wallet

**Solution:**
1. **Check Wallet Installation:**
   - Open browser extensions
   - Verify wallet is enabled
   - Try disabling other wallet extensions temporarily

2. **Browser Compatibility:**
   - Use Chrome, Brave, or Firefox
   - Avoid Safari (limited support)

3. **Restart Browser:**
   - Close all browser windows
   - Reopen and try again

---

## 🔧 **Configuration Check**

### **Environment Variables (Should be set):**
```bash
NEXT_PUBLIC_SOLANA_NETWORK=devnet
NEXT_PUBLIC_SOLANA_RPC_URL=https://api.devnet.solana.com
NEXT_PUBLIC_RPC_ENDPOINT=https://api.devnet.solana.com
```

### **Wallet Adapters Configured:**
- ✅ Phantom (auto-detected via Wallet Standard)
- ✅ Solflare (explicitly added)
- ✅ Other wallets auto-detected

---

## 🧪 **Testing Steps**

### **Step 1: Verify Environment**
```bash
curl http://localhost:3003/api/health
```
Should show:
```json
{
  "status": "healthy",
  "services": {
    "env_variables": {
      "NEXT_PUBLIC_SOLANA_NETWORK": true
    }
  }
}
```

### **Step 2: Check Browser Console**
1. Open Developer Tools (F12)
2. Go to Console tab
3. Look for wallet-related errors
4. Check for `[wallet:phantom]` messages

### **Step 3: Test Wallet Connection**
1. Click "Connect Wallet" button
2. Select your wallet from the modal
3. Approve the connection in the wallet extension
4. Should see wallet address appear

---

## 🔄 **Quick Fix Steps**

### **If Nothing Works:**
1. **Reset Everything:**
   ```bash
   # Clear browser data
   localStorage.clear()
   sessionStorage.clear()
   ```

2. **Restart Services:**
   ```bash
   pkill -f "next dev"
   npm run dev
   ```

3. **Try Different Wallet:**
   - Install Phantom if using Solflare
   - Install Solflare if using Phantom

---

## 📱 **Mobile Wallet Support**

### **For Mobile Testing:**
1. **Install Mobile Wallet:**
   - Phantom iOS/Android app
   - Solflare mobile app

2. **Use WalletConnect:**
   - QR code scanning
   - Deep linking support

3. **Browser Support:**
   - Mobile Chrome (Android)
   - Mobile Safari (iOS - limited)

---

## 🛠️ **Advanced Debugging**

### **Check Wallet Provider:**
```javascript
// In browser console
console.log('Network:', window.solana?.network)
console.log('Is Connected:', window.solana?.isConnected)
console.log('Public Key:', window.solana?.publicKey?.toString())
```

### **Check RPC Connection:**
```javascript
// Test RPC endpoint
fetch('https://api.devnet.solana.com')
  .then(r => r.json())
  .then(console.log)
```

---

## 🆘 **Get Help**

### **Still Having Issues?**
1. **Check Console Logs** for specific error messages
2. **Verify Network** is set to Devnet
3. **Ensure Wallet** is unlocked and installed
4. **Try Different Browser** or wallet

### **Common Error Messages:**
- `"Wallet not ready"` → Install/unlock wallet
- `"Failed to connect"` → Check network settings
- `"Wallet not detected"` → Restart browser
- `"Network mismatch"` → Change wallet to Devnet

---

## ✅ **Success Indicators**

### **Working Connection Should Show:**
- ✅ Wallet modal opens when clicking "Connect"
- ✅ Wallet appears in the selection list
- ✅ Connection request appears in wallet extension
- ✅ Wallet address displays after connection
- ✅ Balance shows (if wallet has SOL)

---

**🎯 Most Common Fix:** Switch wallet to **Devnet** and refresh the page!
