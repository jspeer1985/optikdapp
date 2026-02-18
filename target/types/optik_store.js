/**
 * optik_store.js
 *
 * Central store service for merchant actions.
 * Handles API communication, validation, and pipeline triggers.
 */

class OptikStore {
    constructor(config = {}) {
        this.apiBase = config.apiBase || "/api";
        this.merchantId = config.merchantId || null;
        this.authToken = config.authToken || null;
    }

    // -------------------------
    // INTERNAL REQUEST HANDLER
    // -------------------------
    async request(endpoint, method = "GET", body = null) {
        const headers = {
            "Content-Type": "application/json",
        };

        if (this.authToken) {
            headers["Authorization"] = `Bearer ${this.authToken}`;
        }

        const response = await fetch(`${this.apiBase}${endpoint}`, {
            method,
            headers,
            body: body ? JSON.stringify(body) : null,
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API Error: ${errorText}`);
        }

        return response.json();
    }

    // -------------------------
    // STORE MANAGEMENT
    // -------------------------
    async createStore(storeData) {
        if (!this.merchantId) {
            throw new Error("Merchant ID is required.");
        }

        return this.request("/stores/create", "POST", {
            merchantId: this.merchantId,
            ...storeData,
        });
    }

    async getStore() {
        return this.request(`/stores/${this.merchantId}`);
    }

    // -------------------------
    // PRODUCT MANAGEMENT
    // -------------------------
    async createProduct(productData) {
        if (!productData.name || !productData.price) {
            throw new Error("Product name and price are required.");
        }

        return this.request("/products/create", "POST", {
            merchantId: this.merchantId,
            ...productData,
        });
    }

    async listProducts() {
        return this.request(`/products?merchantId=${this.merchantId}`);
    }

    // -------------------------
    // NFT PIPELINE
    // -------------------------
    async mintProductNFT(productId) {
        return this.request("/nft/mint", "POST", {
            merchantId: this.merchantId,
            productId,
        });
    }

    // -------------------------
    // PAYMENTS
    // -------------------------
    async configurePayments(settings) {
        return this.request("/payments/configure", "POST", {
            merchantId: this.merchantId,
            ...settings,
        });
    }

    async withdrawFunds() {
        return this.request("/payments/withdraw", "POST", {
            merchantId: this.merchantId,
        });
    }

    // -------------------------
    // ANALYTICS
    // -------------------------
    async getAnalytics() {
        return this.request(`/analytics?merchantId=${this.merchantId}`);
    }

    // -------------------------
    // STAKING
    // -------------------------
    async stakeTokens(amount) {
        return this.request("/staking/stake", "POST", {
            merchantId: this.merchantId,
            amount,
        });
    }

    async getStakingStatus() {
        return this.request(`/staking/status?merchantId=${this.merchantId}`);
    }

    // -------------------------
    // OPTIKGPT INTEGRATION
    // -------------------------
    async askAssistant(message) {
        return this.request("/assistant/query", "POST", {
            merchantId: this.merchantId,
            message,
        });
    }
}

export default OptikStore;
