import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axiosClient from '../api/axiosClient';

const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setError(''); 
        try {
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            const response = await axiosClient.post('/api/auth/login', formData, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            });

            console.log('Login response', response.status, response.data);

            if (response.status === 200 && response.data?.access_token) {
                localStorage.setItem('access_token', response.data.access_token);
                navigate('/');
            } else {
                setError('Đăng nhập thất bại: token không hợp lệ');
            }

        } catch (err) {
            console.error("Lỗi đăng nhập API:", err.response?.data);
            
            const detailData = err?.response?.data?.detail;
            
            // Xử lý triệt để đống Object của FastAPI giống trang Đăng ký
            if (Array.isArray(detailData)) {
                setError(`Lỗi nhập liệu: ${detailData[0].msg}`);
            } 
            // Xử lý lỗi text bình thường (VD: "Sai tài khoản hoặc mật khẩu")
            else if (typeof detailData === 'string') {
                setError(detailData);
            } 
            // Chặn đứng các lỗi không xác định
            else {
                setError('Sai tài khoản hoặc mật khẩu, vui lòng thử lại!');
            }
        }
    };

    // CHƠI HỆ CSS THUẦN (INLINE STYLES)
    const styles = {
        container: {
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: '#f3f4f6',
            fontFamily: 'sans-serif'
        },
        card: {
            backgroundColor: '#ffffff',
            padding: '40px',
            borderRadius: '12px',
            boxShadow: '0 10px 25px rgba(0, 0, 0, 0.1)',
            width: '100%',
            maxWidth: '400px'
        },
        title: {
            textAlign: 'center',
            margin: '0 0 5px 0',
            color: '#1f2937',
            fontSize: '28px',
            fontWeight: 'bold'
        },
        subtitle: {
            textAlign: 'center',
            color: '#6b7280',
            margin: '0 0 30px 0',
            fontSize: '14px'
        },
        errorBox: {
            backgroundColor: '#fee2e2',
            border: '1px solid #f87171',
            color: '#b91c1c',
            padding: '10px',
            borderRadius: '6px',
            marginBottom: '20px',
            textAlign: 'center',
            fontSize: '14px'
        },
        formGroup: {
            marginBottom: '20px'
        },
        label: {
            display: 'block',
            marginBottom: '8px',
            color: '#374151',
            fontSize: '14px',
            fontWeight: '600'
        },
        input: {
            width: '100%',
            padding: '12px',
            border: '1px solid #d1d5db',
            borderRadius: '8px',
            boxSizing: 'border-box',
            fontSize: '15px',
            outline: 'none',
            transition: 'border-color 0.2s'
        },
        button: {
            width: '100%',
            padding: '12px',
            backgroundColor: '#db2777', // Màu hồng Pink Hat
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: 'bold',
            cursor: 'pointer',
            marginTop: '10px',
            transition: 'background-color 0.2s'
        }
    };

    return (
        <div style={styles.container}>
            <div style={styles.card}>
                
                <h2 style={styles.title}>Đăng nhập</h2>
                
                {error && <div style={styles.errorBox}>{error}</div>}

                <form onSubmit={handleLogin}>
                    <div style={styles.formGroup}>
                        <label style={styles.label}>Tài khoản (Username)</label>
                        <input 
                            type="text" 
                            style={styles.input}
                            placeholder="Nhập tên đăng nhập..." 
                            value={username} 
                            onChange={(e) => setUsername(e.target.value)} 
                            required
                        />
                    </div>

                    <div style={styles.formGroup}>
                        <label style={styles.label}>Mật khẩu (Password)</label>
                        <input 
                            type="password" 
                            style={styles.input}
                            placeholder="••••••••" 
                            value={password} 
                            onChange={(e) => setPassword(e.target.value)} 
                            required
                        />
                    </div>

                    <button 
                        type="submit" 
                        style={styles.button}
                        onMouseOver={(e) => e.target.style.backgroundColor = '#be185d'}
                        onMouseOut={(e) => e.target.style.backgroundColor = '#db2777'}
                    >
                        Đăng nhập
                    </button>
                </form>

                <div style={{ marginTop: 12, textAlign: 'center' }}>
                    <span>Chưa có tài khoản? </span>
                    <a href="/register" style={{ color: '#db2777', textDecoration: 'none' }}>Đăng ký ngay</a>
                </div>

            </div>
        </div>
    );
};

export default Login;