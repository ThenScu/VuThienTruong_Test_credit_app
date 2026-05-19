import React, { useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom'; // 👈 Nạp vũ khí mới
import api from '../api/axiosClient';

const Tools = () => {
    // 💥 Nắm lấy cái dây cáp từ MainLayout truyền xuống
    const { refreshProfile } = useOutletContext() || {}; 
    
    const [unlockedFeatures, setUnlockedFeatures] = useState([]);
    const [loading, setLoading] = useState(true);
    const [terminalLog, setTerminalLog] = useState('> Hệ thống Technical United sẵn sàng...\n> Chờ lệnh từ Hacker mũ hồng...\n');

    const toolsList = [
        { code: 'BASIC_RECON', name: 'Basic Reconnaissance', path: '/api/services/basic-recon', cost: 100, desc: 'Thu thập thông tin sơ bộ của mục tiêu, dò cổng mở.', icon: '🔍' },
        { code: 'PATH_TRAVERSAL', name: 'Path Traversal Scanner', path: '/api/services/path-traversal', cost: 200, desc: 'Dò tìm lỗ hổng đọc file nhạy cảm (/etc/passwd).', icon: '📂' },
        { code: 'SQLi', name: 'SQL Injection', path: '/api/services/SQLi', cost: 300, desc: 'Khai thác lỗi chèn mã SQL để rút ruột database.', icon: '💉' },
        { code: 'SECRET_SCANNER', name: 'Secret Scanner', path: '/api/services/secret-scanner', cost: 500, desc: 'Quét toàn bộ mã nguồn tìm API Key, Token bị lộ.', icon: '🔑' },
        { code: 'FULL_WEB_PENTEST', name: 'Full Web Pentest', path: '/api/services/full-web-pentest', cost: 1000, desc: 'Tổng tấn công toàn diện hệ thống web từ A-Z.', icon: '🕷️' }
    ];

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const res = await api.get('/api/users/me');
                console.log("🕵️‍♂️ DATA TỪ BACKEND TRẢ VỀ:", res.data); 
                setUnlockedFeatures(res.data.unlocked_features || []);
            } catch (err) {
                console.error('Lỗi check quyền:', err);
            } finally {
                setLoading(false);
            }
        };
        fetchProfile();
    }, []);

    // Hàm check chìa khóa (Đã fix mạnh tay, chấp mọi cấu trúc data)
    const checkUnlocked = (toolCode) => {
        if (!Array.isArray(unlockedFeatures)) return false;
        return unlockedFeatures.some(uf => {
            if (typeof uf === 'string') return uf === toolCode;
            return (
                uf?.code === toolCode || 
                uf?.feature_code === toolCode || 
                uf?.feature?.code === toolCode
            );
        });
    };

    const executeTool = async (tool) => {
        setTerminalLog(prev => prev + `\n> [ĐANG XỬ LÝ] Khởi động vũ khí [${tool.name}]...\n> Đang nã đạn vào mục tiêu...`);
        try {
            const res = await api.get(tool.path);
            setTerminalLog(prev => prev + `\n> [THÀNH CÔNG] ${res.data.message}\n> 💸 Tiêu hao: -${res.data.cost} credits | 💰 Số dư mới: ${res.data.remaining_balance} credits\n`);
            
            // 💥 Xài chiêu cập nhật tiền mượt mà thay cho lệnh reload trang
            if (refreshProfile) {
                refreshProfile();
            }
            
        } catch (err) {
            const errorMsg = err?.response?.data?.detail || 'Thất bại! Kiểm tra lại kết nối hoặc túi tiền.';
            setTerminalLog(prev => prev + `\n> [LỖI] ${errorMsg}\n`);
        }
    };

    // Giao diện đã được trả về bản gốc gọn gàng
    const styles = {
        card: { background: '#fff', padding: '20px', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)', display: 'flex', flexDirection: 'column', height: '100%' },
        terminal: { background: '#111827', color: '#10b981', padding: '15px', borderRadius: '8px', fontFamily: 'monospace', fontSize: '14px', whiteSpace: 'pre-wrap', height: '200px', overflowY: 'auto', marginTop: '10px', boxShadow: 'inset 0 0 10px rgba(0,0,0,0.5)' },
        buttonRun: { padding: '10px', background: '#db2777', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold', marginTop: 'auto', transition: '0.2s' },
        buttonLocked: { padding: '10px', background: '#e5e7eb', color: '#9ca3af', border: 'none', borderRadius: '6px', cursor: 'not-allowed', fontWeight: 'bold', marginTop: 'auto' }
    };

    if (loading) return <div>Đang khởi động radar vũ khí...</div>;

    return (
        <div>
            <h2 style={{ color: '#1f2937', marginBottom: '20px' }}>🛠️ Kho Vũ Khí Pentest</h2>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
                {toolsList.map(tool => {
                    const isUnlocked = checkUnlocked(tool.code);
                    
                    return (
                        <div key={tool.code} style={styles.card}>
                            <h3 style={{ margin: '0 0 10px 0', fontSize: '18px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                {tool.icon} {tool.name}
                            </h3>
                            <p style={{ color: '#6b7280', fontSize: '14px', marginBottom: '15px' }}>{tool.desc}</p>
                            
                            <div style={{ marginBottom: '15px', fontSize: '14px' }}>
                                Tiêu hao: <strong style={{ color: '#dc3545' }}>{tool.cost} Credits</strong>/Lần
                            </div>
                            
                            {isUnlocked ? (
                                <button 
                                    style={styles.buttonRun}
                                    onClick={() => executeTool(tool)}
                                    onMouseOver={(e) => e.target.style.background = '#be185d'}
                                    onMouseOut={(e) => e.target.style.background = '#db2777'}
                                >
                                    🚀 Kích hoạt ({tool.cost} cr)
                                </button>
                            ) : (
                                <button style={styles.buttonLocked} disabled>
                                    🔒 Đã Khóa (Cần mua gói)
                                </button>
                            )}
                        </div>
                    );
                })}
            </div>

            {/* 💥 FIX Ở ĐÂY: Tăng marginTop lên 60px để đẩy Terminal xuống */}
            <h3 style={{ marginTop: '60px', marginBottom: '10px', color: '#1f2937' }}>🖥️ System Log</h3>
            <div style={styles.terminal}>
                {terminalLog}
            </div>
        </div>
    );
};

export default Tools;