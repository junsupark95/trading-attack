import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const Dashboard: React.FC = () => {
    const [status, setStatus] = useState<any>(null);
    const [positions, setPositions] = useState([]);
    const [isEmergency, setIsEmergency] = useState(false);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [sRes, pRes] = await Promise.all([
                    axios.get(`${API_BASE}/status`),
                    axios.get(`${API_BASE}/positions`)
                ]);
                setStatus(sRes.data);
                setPositions(pRes.data);
                setIsEmergency(sRes.data.emergency_stop);
            } catch (err) {
                console.error("Failed to fetch dashboard data", err);
            }
        };

        const interval = setInterval(fetchData, 2000);
        return () => clearInterval(interval);
    }, []);

    const triggerStop = async () => {
        if (window.confirm("정말로 모든 주문을 중단하고 긴급 정지하시겠습니까?")) {
            await axios.post(`${API_BASE}/emergency-stop`);
            setIsEmergency(true);
        }
    };

    return (
        <div style={{ padding: '20px', fontFamily: 'Inter, sans-serif', backgroundColor: '#0f172a', color: '#f8fafc', minHeight: '100vh' }}>
            <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #334155', paddingBottom: '20px' }}>
                <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                    KAOM Trading Dashboard 
                    <span style={{ fontSize: '0.9rem', marginLeft: '10px', color: status?.is_real_trading ? '#ef4444' : '#10b981' }}>
                        [{status?.is_real_trading ? 'LIVE' : 'PAPER'}]
                    </span>
                </h1>
                <button 
                    onClick={triggerStop}
                    disabled={isEmergency}
                    style={{
                        backgroundColor: isEmergency ? '#64748b' : '#ef4444',
                        color: 'white',
                        padding: '10px 20px',
                        borderRadius: '6px',
                        border: 'none',
                        cursor: 'pointer',
                        fontWeight: 'bold'
                    }}
                >
                    {isEmergency ? 'SYSTEM HALTED' : 'EMERGENCY STOP'}
                </button>
            </header>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', marginTop: '30px' }}>
                {/* System Status Card */}
                <div style={{ backgroundColor: '#1e293b', padding: '20px', borderRadius: '12px', border: '1px solid #334155' }}>
                    <h2 style={{ fontSize: '1.1rem', marginBottom: '15px', color: '#94a3b8' }}>System Status</h2>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                        <span>Current State:</span>
                        <span style={{ fontWeight: 'bold', color: '#38bdf8' }}>{status?.state}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span>Daily Loss Limit:</span>
                        <span style={{ color: status?.daily_loss_limit_hit ? '#ef4444' : '#10b981' }}>
                            {status?.daily_loss_limit_hit ? 'BREACHED' : 'SAFE'}
                        </span>
                    </div>
                </div>

                {/* Positions Card */}
                <div style={{ backgroundColor: '#1e293b', padding: '20px', borderRadius: '12px', border: '1px solid #334155', gridColumn: 'span 2' }}>
                    <h2 style={{ fontSize: '1.1rem', marginBottom: '15px', color: '#94a3b8' }}>Active Positions</h2>
                    <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
                        <thead>
                            <tr style={{ borderBottom: '1px solid #334155', color: '#64748b' }}>
                                <th style={{ padding: '10px' }}>Symbol</th>
                                <th>Qty</th>
                                <th>Avg Price</th>
                                <th>PnL %</th>
                            </tr>
                        </thead>
                        <tbody>
                            {positions.length > 0 ? positions.map((pos: any) => (
                                <tr key={pos.symbol} style={{ borderBottom: '1px solid #1e293b' }}>
                                    <td style={{ padding: '10px', fontWeight: 'bold' }}>{pos.symbol}</td>
                                    <td>{pos.quantity}</td>
                                    <td>{pos.entry_price.toLocaleString()}</td>
                                    <td style={{ color: pos.pnl_pct >= 0 ? '#10b981' : '#ef4444' }}>
                                        {pos.pnl_pct.toFixed(2)}%
                                    </td>
                                </tr>
                            )) : (
                                <tr>
                                    <td colSpan={4} style={{ textAlign: 'center', padding: '20px', color: '#64748b' }}>No active positions.</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
