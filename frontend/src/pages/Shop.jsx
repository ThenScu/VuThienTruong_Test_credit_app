import React, { useEffect, useState } from 'react';
import api from '../api/axiosClient';
import AdminPackages from './AdminPackages'; // Nhập khẩu kho vũ khí của Admin vào đây

const Shop = () => {
    const [packages, setPackages] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [currentUser, setCurrentUser] = useState(null); // Biến chứa dữ liệu User đang cầm chuột

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                
                // 1. Quét radar xem ai đang truy cập
                const userRes = await api.get('/api/users/me');
                setCurrentUser(userRes.data);

                // 2. Móc danh sách gói từ Database
                const res = await api.get('/api/packages');
                
                // 3. Sắp xếp giá từ thấp đến cao (Fix yêu cầu số 1)
                const sortedPackages = (res.data || []).sort((a, b) => a.price - b.price);
                setPackages(sortedPackages);
                
            } catch (err) {
                console.error('Lỗi lấy data:', err);
                setError('Không thể tải danh sách gói.');
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const handleBuy = async (pkgId) => {
        if (!currentUser) return;
        
        try {
            // FIX CHÍ MẠNG: Dùng ID thật của người đang đăng nhập, dẹp bỏ giả lập user_id: 1
            const payload = { user_id: currentUser.id, package_id: pkgId };
            await api.post('/api/transactions/buy', payload);
            
            alert('Ting ting! Credits đã được cộng vào ví. (F5 lại trang để cập nhật số dư nhé)');
        } catch (err) {
            console.error('Lỗi mua package:', err);
            alert(err?.response?.data?.detail || 'Giao dịch thất bại');
        }
    };

    if (loading) return <div>Đang quét radar hệ thống...</div>;
    if (error) return <div style={{ color: 'red' }}>{error}</div>;

    // ==========================================
    // PHÂN LUỒNG GIAO DIỆN Ở ĐÂY
    // ==========================================
    
    // Nếu là Admin -> Hiện thẳng kho quản lý vũ khí công nghệ (AdminPackages)
    if (currentUser && (currentUser.tier === 'admin' || currentUser.username === 'admin')) {
    return <AdminPackages />;
}

    // Nếu là Newbie/User thường -> Hiện Showroom mua bán
    return (
        <div>
            <h2>🛒 Cửa hàng Packages</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(240px,1fr))', gap: 16 }}>
                {packages.map(p => (
                    <div key={p.id} style={{ background: '#fff', padding: 16, borderRadius: 8, boxShadow: '0 4px 8px rgba(0,0,0,0.05)'}}>
                        <h3 style={{ textTransform: 'capitalize', color: '#1f2937' }}>{p.name}</h3>
                        <p style={{ color: '#6b7280', fontSize: '14px' }}>{p.description}</p>
                        <p style={{ fontSize: '18px', margin: '10px 0' }}>📦 <strong>{p.credits_awarded} credits</strong></p>
                        <p style={{ fontWeight: 'bold' }}>Giá: {p.price.toLocaleString('vi-VN')} VNĐ</p>
                        <button 
                            onClick={() => handleBuy(p.id)} 
                            style={{ padding: '10px 16px', background: '#db2777', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', width: '100%', fontWeight: 'bold', marginTop: '10px' }}
                        >
                            Chốt Gói Này
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Shop;