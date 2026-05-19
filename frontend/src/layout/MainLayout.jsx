import React, { useEffect, useState } from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import api from '../api/axiosClient';

const MainLayout = () => {
    const navigate = useNavigate();
    const [userData, setUserData] = useState(null);

    // 💥 1. Đưa hàm này ra ngoài để tái sử dụng
    const fetchMyProfile = async () => {
        try {
            const response = await api.get('/api/users/me');
            setUserData(response.data);
        } catch (error) {
            console.error("Lỗi lấy thông tin:", error);
            localStorage.removeItem('access_token');
            navigate('/login');
        }
    };

    useEffect(() => {
        fetchMyProfile();
    }, [navigate]);

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        navigate('/login');
    };

    const isAdmin = userData?.username === 'admin' || userData?.tier === 'admin';

    return (
        <div style={{ display: 'flex', minHeight: '100vh', fontFamily: 'sans-serif', color: '#333' }}>
            {/* SIDEBAR */}
            <nav style={{ width: '250px', backgroundColor: '#fff', borderRight: '1px solid #eaeaea', display: 'flex', flexDirection: 'column' }}>
                <div style={{ padding: '20px', fontSize: '1.2rem', fontWeight: 'bold', borderBottom: '1px solid #eaeaea' }}>
                    <span style={{ color: isAdmin ? '#dc3545' : 'inherit' }}>
                        {isAdmin ? '🛡️ Admin Panel' : '🛡️ Technical United'}
                    </span>
                </div>
                <ul style={{ listStyleType: 'none', padding: 0, margin: 0 }}>
                    {isAdmin ? (
                        <li style={{ borderBottom: '1px solid #f5f5f5', backgroundColor: '#fff0f3' }}>
                            <Link to="/shop" style={{ display: 'block', padding: '15px 20px', textDecoration: 'none', color: '#db2777', fontWeight: 'bold' }}>
                                📦 Quản lý Packages
                            </Link>
                        </li>
                    ) : (
                        <>
                            <li style={{ borderBottom: '1px solid #f5f5f5' }}>
                                <Link to="/profile" style={{ display: 'block', padding: '15px 20px', textDecoration: 'none', color: '#555' }}>👤 Hồ Sơ</Link>
                            </li>
                            <li style={{ borderBottom: '1px solid #f5f5f5' }}>
                                <Link to="/shop" style={{ display: 'block', padding: '15px 20px', textDecoration: 'none', color: '#555' }}>🛒 Cửa Hàng</Link>
                            </li>
                            <li style={{ borderBottom: '1px solid #f5f5f5' }}>
                                <Link to="/tools" style={{ display: 'block', padding: '15px 20px', textDecoration: 'none', color: '#555' }}>🛠️ Công Cụ Pentest</Link>
                            </li>
                        </>
                    )}
                </ul>
            </nav>

            {/* KHU VỰC BÊN PHẢI */}
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                <header style={{ backgroundColor: '#fff', padding: '15px 20px', borderBottom: '1px solid #eaeaea', display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
                    <div style={{ marginRight: '20px', fontSize: '0.95rem' }}>
                        {userData ? (
                            <>
                                <span>Xin chào, <strong>{userData.username}</strong></span> | 
                                <span style={{ marginLeft: '10px' }}>Hạng: <strong style={{ color: isAdmin ? '#dc3545' : '#007bff' }}>{userData.tier}</strong></span>
                                {!isAdmin && (
                                    <span style={{ marginLeft: '10px' }}>| Ví: <strong style={{ color: '#28a745' }}>{userData.balance}</strong> Credits</span>
                                )}
                            </>
                        ) : (
                            <span>Đang tải dữ liệu radar...</span>
                        )}
                    </div>
                    <button onClick={handleLogout} style={{ padding: '8px 16px', backgroundColor: '#dc3545', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Đăng xuất</button>
                </header>

                <main style={{ padding: '30px', flex: 1, backgroundColor: '#f8f9fa' }}>
                    {/* 💥 2. BÍ QUYẾT LÀ ĐÂY: Quăng cái dây cáp fetchMyProfile xuống cho các trang con xài */}
                    <Outlet context={{ refreshProfile: fetchMyProfile }} /> 
                </main>
            </div>
        </div>
    );
};

export default MainLayout;