import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Activity, 
  AlertTriangle, 
  TrendingUp, 
  TrendingDown, 
  XOctagon, 
  RefreshCcw,
  LayoutDashboard,
  Wallet
} from 'lucide-react';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const Dashboard: React.FC = () => {
    const [status, setStatus] = useState<any>(null);
    const [positions, setPositions] = useState<any[]>([]);
    const [isEmergency, setIsEmergency] = useState(false);
    const [isLoading, setIsLoading] = useState(true);

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
                setIsLoading(false);
            } catch (err) {
                console.error("Dashboard Sync Error", err);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 3000);
        return () => clearInterval(interval);
    }, []);

    const triggerStop = async () => {
        if (window.confirm("정말로 모든 주문을 중단하고 긴급 정지하시겠습니까? (AI 제어권 박탈)")) {
            await axios.post(`${API_BASE}/emergency-stop`);
            setIsEmergency(true);
        }
    };

    if (isLoading) return (
      <div className="flex items-center justify-center min-h-screen bg-brand-dark">
        <RefreshCcw className="animate-spin text-brand-accent w-10 h-10" />
      </div>
    );

    return (
        <div className="min-h-screen bg-brand-dark pb-20 px-4 md:px-8">
            {/* Header */}
            <header className="flex flex-col md:flex-row justify-between items-start md:items-center py-6 gap-4">
                <div className="flex items-center gap-3">
                    <div className="bg-brand-accent/20 p-2 rounded-xl">
                      <LayoutDashboard className="text-brand-accent w-6 h-6" />
                    </div>
                    <div>
                      <h1 className="text-2xl font-bold tracking-tight text-white">KAOM Dashboard</h1>
                      <div className="flex items-center gap-2 mt-1">
                        <span className={`w-2 h-2 rounded-full ${status?.is_real_trading ? 'bg-brand-danger animate-pulse' : 'bg-brand-success'}`} />
                        <span className="text-xs uppercase font-bold text-slate-400">
                          {status?.is_real_trading ? 'Live Trading Active' : 'Paper Trading Mode'}
                        </span>
                      </div>
                    </div>
                </div>
                
                <button 
                    onClick={triggerStop}
                    disabled={isEmergency}
                    className={`w-full md:w-auto flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-bold transition-all ${
                      isEmergency 
                      ? 'bg-slate-700 text-slate-400 cursor-not-allowed' 
                      : 'bg-brand-danger hover:bg-red-600 hover:shadow-lg hover:shadow-red-900/40 text-white'
                    }`}
                >
                    <XOctagon className="w-5 h-5" />
                    {isEmergency ? 'EMERGENCY HALTED' : 'EMERGENCY STOP'}
                </button>
            </header>

            {/* Quick Stats Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                <StatCard 
                  title="System State" 
                  value={status?.state || 'IDLE'} 
                  icon={<Activity className="text-brand-accent" />}
                />
                <StatCard 
                  title="Daily PnL" 
                  value="+1.24%" 
                  icon={<TrendingUp className="text-brand-success" />}
                  subValue="320,000 KRW"
                />
                <StatCard 
                  title="Risk Status" 
                  value={status?.daily_loss_limit_hit ? 'CRITICAL' : 'SAFE'} 
                  icon={<AlertTriangle className={status?.daily_loss_limit_hit ? 'text-brand-danger' : 'text-brand-success'} />}
                  isUrgent={status?.daily_loss_limit_hit}
                />
                <StatCard 
                  title="Balance" 
                  value="12,450,000" 
                  icon={<Wallet className="text-brand-accent" />}
                  subValue="Reserved: 40%"
                />
            </div>

            {/* Main Content Area */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Positions Table (Responsive) */}
                <div className="lg:col-span-2 glass-card overflow-hidden">
                    <div className="px-6 py-4 border-b border-white/5 flex justify-between items-center">
                      <h2 className="font-bold text-lg">Active Positions</h2>
                      <span className="bg-brand-accent/10 text-brand-accent text-xs px-2 py-1 rounded-md font-mono">
                        {positions.length} SECS
                      </span>
                    </div>
                    <div className="overflow-x-auto">
                      <table className="w-full text-left">
                        <thead>
                          <tr className="text-slate-500 text-sm uppercase tracking-wider">
                            <th className="px-6 py-4 font-semibold">Symbol</th>
                            <th className="px-6 py-4 font-semibold">Qty</th>
                            <th className="px-6 py-4 font-semibold">Entry / Curr</th>
                            <th className="px-6 py-4 font-semibold text-right">PnL</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                          {positions.length > 0 ? positions.map((pos) => (
                            <tr key={pos.symbol} className="hover:bg-white/5 transition-colors">
                              <td className="px-6 py-4 font-bold text-white">{pos.symbol}</td>
                              <td className="px-6 py-4">{pos.quantity}</td>
                              <td className="px-6 py-4">
                                <div className="text-sm font-mono">{pos.entry_price.toLocaleString()}</div>
                                <div className="text-xs text-slate-500">{pos.current_price?.toLocaleString() || '---'}</div>
                              </td>
                              <td className={`px-6 py-4 text-right font-bold ${pos.pnl_pct >= 0 ? 'text-brand-success' : 'text-brand-danger'}`}>
                                {pos.pnl_pct >= 0 ? '+' : ''}{pos.pnl_pct.toFixed(2)}%
                              </td>
                            </tr>
                          )) : (
                            <tr>
                              <td colSpan={4} className="px-6 py-12 text-center text-slate-500 italic">
                                No active positions in the market.
                              </td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                    </div>
                </div>

                {/* Side Info / Logs */}
                <div className="flex flex-col gap-4">
                  <div className="glass-card p-6">
                    <h2 className="font-bold mb-4 flex items-center gap-2">
                       <AlertTriangle className="w-4 h-4 text-brand-accent" />
                       Risk Watch
                    </h2>
                    <ul className="space-y-3 text-sm">
                      <RiskItem label="Max Positions" value={`${positions.length} / 3`} />
                      <RiskItem label="Daily Stop" value="-5.0%" />
                      <RiskItem label="Symbol Stop" value="-2.0%" />
                      <RiskItem label="Market Status" value="OPEN" highlight />
                    </ul>
                  </div>
                  
                  <div className="glass-card p-6 flex-grow">
                    <h2 className="font-bold mb-4">Activity Log</h2>
                    <div className="space-y-4 max-h-[300px] overflow-y-auto scrollbar-hide">
                      <LogItem time="09:05" type="ENTRY" msg="BUY 005930 @ 72,100" />
                      <LogItem time="09:02" type="SCAN" msg="Detected Gap-Up on 035720" />
                      <LogItem time="08:40" type="SYS" msg="Strategy initialized (PAPER)" />
                    </div>
                  </div>
                </div>
            </div>
        </div>
    );
};

// UI Components
const StatCard = ({ title, value, icon, subValue, isUrgent }: any) => (
  <div className={`glass-card p-5 ${isUrgent ? 'ring-2 ring-brand-danger' : ''}`}>
    <div className="flex justify-between items-start mb-2">
      <span className="text-slate-400 text-sm font-medium">{title}</span>
      <div className="bg-slate-800 p-1.5 rounded-lg">{icon}</div>
    </div>
    <div className="text-2xl font-black text-white">{value}</div>
    {subValue && <div className="text-xs text-slate-500 mt-1">{subValue}</div>}
  </div>
);

const RiskItem = ({ label, value, highlight }: any) => (
  <li className="flex justify-between items-center border-b border-white/5 pb-2">
    <span className="text-slate-400">{label}</span>
    <span className={`font-mono font-bold ${highlight ? 'text-brand-accent' : 'text-white'}`}>{value}</span>
  </li>
)

const LogItem = ({ time, type, msg }: any) => (
  <div className="flex gap-3 text-xs border-l-2 border-brand-accent/30 pl-3">
    <span className="text-slate-500 shrink-0">{time}</span>
    <span className="font-bold text-brand-accent shrink-0">[{type}]</span>
    <span className="text-slate-300 break-words">{msg}</span>
  </div>
)

export default Dashboard;
