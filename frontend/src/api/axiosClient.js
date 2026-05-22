import axios from 'axios';

const axiosClient = axios.create({
    baseURL: 'http://localhost:8081', 
    headers: {
        'Content-Type': 'application/json',
    },
});

axiosClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});

// Global response handler: if token expired or unauthorized, clear token and redirect to login
axiosClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            localStorage.removeItem('access_token');
            
            // 🛡️ CHỐT CHẶN Ở ĐÂY: Chỉ ép F5/Redirect nếu KHÔNG PHẢI đang ở trang login
            if (window.location.pathname !== '/login') {
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);

export default axiosClient;