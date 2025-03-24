export class ApiClient {
    constructor(config) {
        this.baseUrl = config.baseUrl;
        this.token = config.token;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = {
            'Accept': 'application/json',
            'Authorization': `Bearer ${this.token}`,
            ...options.headers
        };

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API请求失败:', error);
            throw error;
        }
    }

    async getSymbols() {
        return await this.request('/symbols');
    }

    async getKlineData(symbol, timeframe) {
        return await this.request(`/kline/${symbol}/${timeframe}`);
    }
} 