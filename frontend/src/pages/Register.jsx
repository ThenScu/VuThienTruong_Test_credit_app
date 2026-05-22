import React, { useState } from 'react';
import axiosClient from '../api/axiosClient';
import { useNavigate } from 'react-router-dom';

const Register = () => {
    const [form, setForm] = useState({ username: '', email: '', password: '' });
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError(''); 

        // 🛡️ PHÒNG TUYẾN 1: DÙNG REGEX KIỂM TRA TẠI FRONTEND
        
        // 1. Kiểm tra Email hợp lệ
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(form.email)) {
            setError('Lỗi: Email không đúng định dạng (Ví dụ chuẩn: @gmail.com)');
            return; // Chặn đứng tại đây, không gọi API
        }

        // 2. Kiểm tra Password (Ít nhất 1 chữ IN HOA, 1 chữ số, tối thiểu 6 ký tự)
        const passwordRegex = /^(?=.*[A-Z])(?=.*\d).{6,}$/;
        if (!passwordRegex.test(form.password)) {
            setError('Lỗi: Mật khẩu phải có ít nhất 6 ký tự, bao gồm 1 chữ IN HOA và 1 chữ số');
            return; // Chặn đứng tại đây
        }

        // 🚀 Vượt qua phòng tuyến Frontend thì mới đem quân đi đánh Backend
        try {
            const res = await axiosClient.post('/api/auth/register', form);
            if (res.status === 200 || res.status === 201) {
                alert('Đăng ký thành công! Vui lòng đăng nhập.');
                navigate('/login');
            }
        } catch (err) {
            console.error('Lỗi API trả về:', err.response?.data);
            const detailData = err?.response?.data?.detail;
            
            // 🛡️ PHÒNG TUYẾN 2: BẮT LỖI TỪ BACKEND TRẢ VỀ (Trường hợp email đã tồn tại...)
            if (Array.isArray(detailData)) {
                setError(`Lỗi hệ thống: ${detailData[0].msg}`);
            } else if (typeof detailData === 'string') {
                setError(detailData);
            } else {
                setError('Dữ liệu không hợp lệ, vui lòng kiểm tra lại!');
            }
        }
    }

    // ... (Giữ nguyên phần const styles và return phía dưới không cần đổi)

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
            maxWidth: '420px'
        },
        title: {
            textAlign: 'center',
            margin: '0 0 10px 0',
            color: '#1f2937',
            fontSize: '24px',
            fontWeight: 'bold'
        },
        formGroup: { marginBottom: '14px' },
        label: { display: 'block', marginBottom: '6px', color: '#374151' },
        input: { width: '100%', padding: '10px', border: '1px solid #d1d5db', borderRadius: 8 },
        button: { width: '100%', padding: '12px', backgroundColor: '#db2777', color: '#fff', border: 'none', borderRadius: 8, cursor: 'pointer' },
        errorBox: {
            backgroundColor: '#fee2e2',
            border: '1px solid #f87171',
            color: '#b91c1c',
            padding: '10px',
            borderRadius: '6px',
            marginBottom: '20px',
            textAlign: 'center',
            fontSize: '14px'
        }
    };

    return (
        <div style={styles.container}>
            <div style={styles.card}>
                <h2 style={styles.title}>Đăng ký</h2>
                
                {/* Khối in lỗi được update style lại cho đẹp và an toàn */}
                {error && <div style={styles.errorBox}>{error}</div>}
                
                <form onSubmit={handleSubmit}>
                    <div style={styles.formGroup}>
                        <label style={styles.label}>Username</label>
                        <input style={styles.input} value={form.username} onChange={e => setForm({...form, username: e.target.value})} required />
                    </div>
                    <div style={styles.formGroup}>
                        <label style={styles.label}>Email</label>
                        <input style={styles.input} value={form.email} onChange={e => setForm({...form, email: e.target.value})} required />
                    </div>
                    <div style={styles.formGroup}>
                        <label style={styles.label}>Password</label>
                        <input style={styles.input} type="password" value={form.password} onChange={e => setForm({...form, password: e.target.value})} required />
                    </div>
                    <div style={{ marginTop: 12 }}>
                        <button type="submit" style={styles.button}>Đăng ký</button>
                    </div>
                </form>
                <div style={{ marginTop: 12, textAlign: 'center' }}>
                    <a href="/login" style={{ color: '#db2777', fontWeight: '500', textDecoration: 'none' }}>Quay về đăng nhập</a>
                </div>
            </div>
        </div>
    )
}

export default Register;