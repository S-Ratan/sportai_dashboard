import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import './styles.css';
import { supabase } from './supabaseClient';
import VideoSkeletonOverlay from './VideoSkeletonOverlay';
import {
  Sparkles,
  AlertTriangle,
  Activity,
  Gauge,
  BarChart3,
  ShieldCheck,
  LogOut,
  UserCheck,
  History,
  Upload,
  Trash2,
  FileText,
  ChevronRight,
  ArrowLeft,
  TrendingUp,
  Zap,
  Target,
  Brain,
  Video,
  LineChart,
  MoreVertical
} from 'lucide-react';
import {
  LineChart as RechartsLineChart,
  Line,
  BarChart as RechartsBarChart,
  Bar,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8001').replace(/\/$/, '');

const DEMO_DASHBOARD = {
  kpis: { performanceScore: 78, movementRisk: 32, asymmetry: 18, fatigue: 45 },
  biomechanicsMetrics: [
    { joint: 'Knee', leftSide: 78, rightSide: 71 },
    { joint: 'Hip', leftSide: 66, rightSide: 62 },
    { joint: 'Ankle', leftSide: 54, rightSide: 58 },
    { joint: 'Shoulder', leftSide: 72, rightSide: 68 },
  ],
  movementRiskFactors: [
    { factor: 'Knee Valgus', severity: 'High', score: 68 },
    { factor: 'Hip Drop', severity: 'Medium', score: 45 },
    { factor: 'Trunk Rotation', severity: 'Low', score: 25 },
  ],
  aiCoachTips: [
    { title: 'Knee Alignment', priority: 'High', recommendation: 'Focus on keeping knees aligned over toes during lateral movements. Add 3×10 single-leg squats daily.' },
    { title: 'Hip Stability', priority: 'Medium', recommendation: 'Strengthen glute medius with band walks and lateral lunges to improve hip control.' },
    { title: 'Fatigue Management', priority: 'High', recommendation: 'Your fatigue level is rising. Consider extending rest intervals or reducing training volume.' },
  ],
  historicalTrend: [
    { date: 'Mon', performance: 70 }, { date: 'Tue', performance: 73 }, { date: 'Wed', performance: 71 },
    { date: 'Thu', performance: 75 }, { date: 'Fri', performance: 74 }, { date: 'Sat', performance: 78 }, { date: 'Sun', performance: 78 },
  ],
  videoAnalysisData: { lastAnalyzed: '2024-08-13 14:30', framesProcessed: 1240, detectionRate: 98.5, videoName: 'Training Session_Aug13.mp4' },
};

function toDashboardSeverity(severity) {
  const normalized = String(severity || '').toLowerCase();
  if (normalized === 'moderate') return 'Medium';
  if (normalized === 'high') return 'High';
  return 'Low';
}

function formatBackendDetail(detail) {
  if (typeof detail === 'string') return detail;
  if (detail) return JSON.stringify(detail);
  return 'No additional detail was returned by the backend.';
}

function normalizedJointAngle(angle) {
  return typeof angle === 'number' ? Math.round((angle / 180) * 10000) / 100 : undefined;
}

function buildDashboardData(analysis, reports, videoName) {
  const latest = analysis || reports[0]?.pose_data;
  if (!latest) return { ...DEMO_DASHBOARD, isDemo: true };
  const metrics = latest.injury_risk?.metrics || latest.performance?.metrics || {};
  const summary = latest.biomechanics_summary || {};
  const sessions = reports.slice(0, 7).reverse();
  const trend = sessions.map((report) => ({
    date: new Date(report.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
    performance: report.performance_score,
    risk: report.injury_risk_score,
    confidence: report.analysis_confidence ?? report.pose_data?.analysis_confidence,
  }));
  return {
    kpis: {
      performanceScore: latest.performance?.performance_score ?? reports[0]?.performance_score ?? '—',
      movementRisk: latest.injury_risk?.risk_score ?? reports[0]?.injury_risk_score ?? '—',
      asymmetry: metrics.average_knee_asymmetry ?? '—',
      fatigue: latest.analysis_confidence ?? reports[0]?.analysis_confidence ?? '—',
    },
    historicalTrend: trend,
    biomechanicsMetrics: [
      { joint: 'Knee', leftSide: latest.biomechanics_chart?.knee?.left ?? normalizedJointAngle(summary.left_knee?.avg_angle), rightSide: latest.biomechanics_chart?.knee?.right ?? normalizedJointAngle(summary.right_knee?.avg_angle) },
      { joint: 'Hip', leftSide: latest.biomechanics_chart?.hip?.left ?? normalizedJointAngle(summary.left_hip?.avg_angle), rightSide: latest.biomechanics_chart?.hip?.right ?? normalizedJointAngle(summary.right_hip?.avg_angle) },
      { joint: 'Ankle', leftSide: latest.biomechanics_chart?.ankle?.left, rightSide: latest.biomechanics_chart?.ankle?.right },
      { joint: 'Shoulder', leftSide: latest.biomechanics_chart?.shoulder?.left, rightSide: latest.biomechanics_chart?.shoulder?.right },
    ],
    movementRiskFactors: (latest.recommendations || []).map((item) => ({
      factor: item.category,
      severity: toDashboardSeverity(item.severity),
      score: Math.min(100, Math.round((item.observed_value / item.threshold) * 50)),
    })),
    aiCoachTips: (latest.recommendations || []).map((item) => ({
      title: item.category,
      priority: toDashboardSeverity(item.severity),
      recommendation: item.recommendation,
    })),
    videoAnalysisData: {
      lastAnalyzed: analysis ? new Date().toLocaleString() : reports[0]?.created_at ? new Date(reports[0].created_at).toLocaleString() : 'No completed analysis',
      framesProcessed: latest.frames ?? '—',
      detectionRate: latest.pose_detection_rate ?? reports[0]?.pose_detection_rate ?? '—',
      videoName: videoName || reports[0]?.video_name || 'No completed analysis',
    },
    isDemo: false,
  };
}

/* --- PS-02 Dashboard Component --- */
function PS02Dashboard({ analysis, videoUrl, videoName, userId, onReanalyze }) {
  const [reports, setReports] = useState([]);
  const [dashboardError, setDashboardError] = useState('');
  useEffect(() => {
    if (!userId) return;
    supabase.from('analysis_reports').select('*').eq('user_id', userId)
      .order('created_at', { ascending: false }).then(({ data, error }) => {
        if (error) setDashboardError('Dashboard data could not be loaded.');
        else setReports(data || []);
      });
  }, [userId, analysis]);
  const dashboardData = buildDashboardData(analysis, reports, videoName);
  // KPI Card Component
  function DashboardKPICard({ title, value, suffix, icon: Icon, trendUp = true, color = 'green' }) {
    const colorClass = color === 'green' ? 'kpi-green' : color === 'orange' ? 'kpi-orange' : 'kpi-red';
    return (
      <div className={`kpi-card ${colorClass}`}>
        <div className="kpi-top">
          <span className="kpi-title">{title}</span>
          {Icon && <Icon size={20} className="kpi-icon" />}
        </div>
        <div className="kpi-value">{value}<span className="kpi-suffix">{suffix}</span></div>
        <div className="kpi-trend">
          <TrendingUp size={14} className={trendUp ? 'trend-up' : 'trend-down'} />
          <span>{trendUp ? '+2.5%' : '-1.2%'} from last session</span>
        </div>
      </div>
    );
  }

  // Video Analysis Panel
  function VideoAnalysisPanel() {
    const data = dashboardData.videoAnalysisData;
    return (
      <div className="card">
        <div className="card-header">
          <h3><Video size={20} style={{ marginRight: '8px' }} /> Video Analysis</h3>
        </div>
        <div className="panel-content">
          <div className="analysis-stat-row">
            <div className="analysis-stat">
              <span className="stat-label">Last Analyzed</span>
              <span className="stat-value-large">{data.lastAnalyzed}</span>
            </div>
            <div className="analysis-stat">
              <span className="stat-label">Frames Processed</span>
              <span className="stat-value-large">{data.framesProcessed}</span>
            </div>
            <div className="analysis-stat">
              <span className="stat-label">Detection Rate</span>
              <span className="stat-value-large">{typeof data.detectionRate === 'number' ? `${data.detectionRate.toFixed(1)}%` : data.detectionRate}</span>
            </div>
          </div>
          <div className="video-info">
            <FileText size={16} />
            <div>
              <p className="video-name">{data.videoName}</p>
              <p className="video-meta">Training session • High quality</p>
            </div>
          </div>
          <button className="outline" onClick={onReanalyze} style={{ width: '100%', marginTop: '12px' }}>
            <Upload size={16} style={{ marginRight: '8px' }} /> Re-analyze Video
          </button>
        </div>
      </div>
    );
  }

  // Biomechanics Chart Panel
  function BiomechanicsPanel() {
    return (
      <div className="card">
        <div className="card-header">
          <h3><Activity size={20} style={{ marginRight: '8px' }} /> Biomechanics Analysis</h3>
        </div>
        <div className="panel-content">
          <ResponsiveContainer width="100%" height={280}>
            <RechartsBarChart data={dashboardData.biomechanicsMetrics}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="joint" stroke="#94a3b8" />
              <YAxis domain={[0, 100]} stroke="#94a3b8" />
              <Tooltip 
                contentStyle={{ background: '#1e293b', border: '1px solid #334155' }}
                cursor={{ fill: 'rgba(16, 185, 129, 0.1)' }}
              />
              <Legend />
              <Bar dataKey="leftSide" name="Left Side" fill="#10b981" radius={[4, 4, 0, 0]} />
              <Bar dataKey="rightSide" name="Right Side" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </RechartsBarChart>
          </ResponsiveContainer>
          <div className="biomechanics-legend">
            <div><span className="color-box" style={{ background: '#10b981' }}></span> Left Side</div>
            <div><span className="color-box" style={{ background: '#3b82f6' }}></span> Right Side</div>
          </div>
        </div>
      </div>
    );
  }

  // Movement Risk Panel
  function MovementRiskPanel() {
    const riskColors = {
      'High': '#ef4444',
      'Medium': '#f59e0b',
      'Low': '#10b981'
    };

    return (
      <div className="card">
        <div className="card-header">
          <h3><AlertTriangle size={20} style={{ marginRight: '8px' }} /> Movement Risk Assessment</h3>
        </div>
        <div className="panel-content">
          {dashboardData.movementRiskFactors.length ? dashboardData.movementRiskFactors.map((item, idx) => (
            <div key={idx} className="risk-factor-item">
              <div className="risk-factor-header">
                <span className="risk-factor-name">{item.factor}</span>
                <span className="risk-badge" style={{ borderColor: riskColors[item.severity], color: riskColors[item.severity] }}>
                  {item.severity}
                </span>
              </div>
              <div className="progress-bar-container">
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${item.score}%`, background: riskColors[item.severity] }} 
                  />
                </div>
                <span className="score-label">{item.score}/100</span>
              </div>
            </div>
          )) : <p className="muted">No calculated risk factors are available.</p>}
        </div>
      </div>
    );
  }

  // AI Coach Panel
  function AICoachPanel() {
    const priorityColors = {
      'High': '#ef4444',
      'Medium': '#f59e0b',
      'Low': '#10b981'
    };

    return (
      <div className="card">
        <div className="card-header">
          <h3><Brain size={20} style={{ marginRight: '8px' }} /> AI Coach Recommendations</h3>
        </div>
        <div className="panel-content">
          {dashboardData.aiCoachTips.length ? dashboardData.aiCoachTips.map((tip, idx) => (
            <div key={idx} className="coach-tip">
              <div className="tip-header">
                <span className="tip-title">{tip.title}</span>
                <span className="priority-badge" style={{ borderColor: priorityColors[tip.priority], color: priorityColors[tip.priority] }}>
                  {tip.priority}
                </span>
              </div>
              <p className="tip-content">{tip.recommendation}</p>
            </div>
          )) : <p className="muted">Recommendations appear after a completed analysis.</p>}
        </div>
      </div>
    );
  }

  // Historical Trend Panel
  function HistoricalTrendPanel() {
    return (
      <div className="card">
        <div className="card-header">
          <h3><LineChart size={20} style={{ marginRight: '8px' }} /> 7-Day Trends</h3>
        </div>
        <div className="panel-content">
          <ResponsiveContainer width="100%" height={320}>
            <RechartsLineChart data={dashboardData.historicalTrend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="date" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip 
                contentStyle={{ background: '#1e293b', border: '1px solid #334155' }}
                cursor={{ fill: 'rgba(16, 185, 129, 0.1)' }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="performance" 
                stroke="#10b981" 
                strokeWidth={2}
                dot={{ fill: '#10b981', r: 4 }}
                activeDot={{ r: 6 }}
                name="Performance"
              />
              <Line 
                type="monotone" 
                dataKey="risk" 
                stroke="#ef4444" 
                strokeWidth={2}
                dot={{ fill: '#ef4444', r: 4 }}
                activeDot={{ r: 6 }}
                name="Movement Risk"
              />
              <Line 
                type="monotone" 
                dataKey="confidence" 
                stroke="#f59e0b" 
                strokeWidth={2}
                dot={{ fill: '#f59e0b', r: 4 }}
                activeDot={{ r: 6 }}
                name="Analysis Confidence"
              />
            </RechartsLineChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* KPI Cards Row */}
      <section className="kpi-section">
        <DashboardKPICard 
          title="Performance Score" 
          value={dashboardData.kpis.performanceScore} 
          suffix="/100" 
          icon={Gauge}
          trendUp={true}
          color="green"
        />
        <DashboardKPICard 
          title="Movement Risk" 
          value={dashboardData.kpis.movementRisk} 
          suffix="/100" 
          icon={AlertTriangle}
          trendUp={false}
          color="orange"
        />
        <DashboardKPICard 
          title="Asymmetry" 
          value={dashboardData.kpis.asymmetry} 
          suffix="/100" 
          icon={BarChart3}
          trendUp={false}
          color="orange"
        />
        <DashboardKPICard 
          title={dashboardData.isDemo ? 'Fatigue Level' : 'Analysis Confidence'}
          value={dashboardData.kpis.fatigue} 
          suffix="/100" 
          icon={Zap}
          trendUp={true}
          color="red"
        />
      </section>

      {/* Main Grid Layout */}
      <div className="dashboard-grid">
        <VideoAnalysisPanel />
        <BiomechanicsPanel />
        <MovementRiskPanel />
        <AICoachPanel />
        <div style={{ gridColumn: '1 / -1' }}>
          <HistoricalTrendPanel />
        </div>
      </div>
      {dashboardError && <p className="muted" style={{ color: '#ef4444' }}>{dashboardError}</p>}
      {analysis && <VideoSkeletonOverlay analysis={analysis} videoUrl={videoUrl} videoName={videoName} />}
    </div>
  );
}

/* --- UI Helper Components --- */
function Stat({ title, value, suffix = '', icon: Icon, warning = false }) {
  return (
    <div className={`stat-card ${warning ? 'warning' : ''}`}>
      <div className="stat-header">
        <span className="stat-title">{title}</span>
        {Icon && <Icon size={18} className="stat-icon" />}
      </div>
      <div className="stat-value">
        {value}
        <span className="stat-suffix">{suffix}</span>
      </div>
    </div>
  );
}

function Card({ title, children }) {
  return (
    <div className="card">
      {title && <h3>{title}</h3>}
      {children}
    </div>
  );
}

function Risk({ name, score, level }) {
  return (
    <div className="risk-item">
      <div className="risk-info">
        <span>{name}</span>
        <b>{level}</b>
      </div>
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${Math.min(score, 100)}%` }} />
      </div>
    </div>
  );
}

/* --- Report Display Component --- */
function AnalysisReportView({ analysis }) {
  if (!analysis) return null;

  return (
    <>
      <section className="stats">
        <Stat
          title="Performance Score"
          value={analysis.performance?.performance_score ?? '-'}
          suffix="/100"
          icon={Gauge}
        />
        <Stat
          title="Performance Level"
          value={analysis.performance?.performance_level ?? '-'}
          icon={BarChart3}
        />
        <Stat
          title="Injury Risk Score"
          value={analysis.injury_risk?.risk_score ?? '-'}
          suffix="/100"
          icon={ShieldCheck}
          warning
        />
        <Stat
          title="Risk Level"
          value={analysis.injury_risk?.risk_level ?? '-'}
          icon={AlertTriangle}
          warning
        />
        <Stat
          title="Analysis Confidence"
          value={analysis.analysis_confidence ?? '-'}
          suffix="/100"
          icon={Target}
        />
      </section>

      <div className="grid-2">
        <Card title="Pose Analysis">
          <Risk
            name="Pose Detection Rate"
            score={analysis.pose_detection_rate ?? ((analysis.detected_frames || 0) / (analysis.frames || 1)) * 100}
            level={analysis.frames != null ? `${analysis.detected_frames || 0} / ${analysis.frames || 0} frames` : `${analysis.pose_detection_rate ?? 0}%`}
          />
          <Risk
            name="Knee Angle"
            score={Math.min(analysis.average_knee_angle || 0, 180) / 1.8}
            level={`${analysis.average_knee_angle || 0}°`}
          />
          <Risk
            name="Hip Angle"
            score={Math.min(analysis.average_hip_angle || 0, 180) / 1.8}
            level={`${analysis.average_hip_angle || 0}°`}
          />
          <Risk
            name="Elbow Angle"
            score={Math.min(analysis.average_elbow_angle || 0, 180) / 1.8}
            level={`${analysis.average_elbow_angle || 0}°`}
          />
        </Card>

        <Card title="Injury Risk Factors">
          {analysis.injury_risk?.factors?.length > 0 ? (
            analysis.injury_risk.factors.map((factor, index) => (
              <div className="rec" key={index}>
                <div className="rec-icon">
                  <AlertTriangle size={16} />
                </div>
                <div>
                  <b>{factor}</b>
                  <span>Detected during motion tracking</span>
                </div>
              </div>
            ))
          ) : (
            <p className="muted">No critical risk factors detected.</p>
          )}
        </Card>
      </div>

      <div className="grid-2 mt-20">
        <Card title="Performance Factors">
          {analysis.performance?.factors?.length > 0 ? (
            analysis.performance.factors.map((factor, index) => (
              <div className="rec" key={index}>
                <div className="rec-icon" style={{ background: 'rgba(16, 185, 129, 0.1)', color: '#10b981' }}>
                  <Activity size={16} />
                </div>
                <div>
                  <b>{factor}</b>
                  <span>Movement efficiency indicator</span>
                </div>
              </div>
            ))
          ) : (
            <p className="muted">No performance factors flagged.</p>
          )}
        </Card>

        <Card title="Biomechanics & Asymmetry">
          <div className="movement">
            <div className="movement-top">
              <span>Knee Asymmetry</span>
              <b>{analysis.injury_risk?.metrics?.average_knee_asymmetry ?? '-'}°</b>
            </div>
          </div>
          <div className="movement">
            <div className="movement-top">
              <span>Hip Asymmetry</span>
              <b>{analysis.injury_risk?.metrics?.average_hip_asymmetry ?? '-'}°</b>
            </div>
          </div>
          <div className="movement">
            <div className="movement-top">
              <span>Elbow Asymmetry</span>
              <b>{analysis.injury_risk?.metrics?.average_elbow_asymmetry ?? '-'}°</b>
            </div>
          </div>
          <div className="movement">
            <div className="movement-top">
              <span>Trunk Tilt</span>
              <b>{analysis.injury_risk?.metrics?.average_trunk_tilt ?? '-'}°</b>
            </div>
          </div>
        </Card>
      </div>
    </>
  );
}

/* --- History View Component --- */
function HistoryView({ userId }) {
  const [reports, setReports] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [selectedReport, setSelectedReport] = useState(null);
  const [fetchError, setFetchError] = useState('');

  const fetchReports = async () => {
    setLoadingHistory(true);
    setFetchError('');
    try {
      const { data, error } = await supabase
        .from('analysis_reports')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false });

      if (error) throw error;
      setReports(data || []);
    } catch (err) {
      console.error('Error fetching history:', err.message);
      setFetchError('Failed to load analysis history.');
    } finally {
      setLoadingHistory(false);
    }
  };

  useEffect(() => {
    if (userId) {
      fetchReports();
    }
  }, [userId]);

  const handleDelete = async (e, reportId) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this report?')) return;

    try {
      const { error } = await supabase
        .from('analysis_reports')
        .delete()
        .eq('id', reportId);

      if (error) throw error;
      setReports((prev) => prev.filter((r) => r.id !== reportId));
      if (selectedReport?.id === reportId) {
        setSelectedReport(null);
      }
    } catch (err) {
      alert('Failed to delete report: ' + err.message);
    }
  };

  if (selectedReport) {
    return (
      <div>
        <button
          className="outline mb-20"
          onClick={() => setSelectedReport(null)}
          style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}
        >
          <ArrowLeft size={16} /> Back to History
        </button>

        <Card title={`Report: ${selectedReport.video_name}`}>
          <p className="muted mb-15">
            Analyzed on: {new Date(selectedReport.created_at).toLocaleString()}
          </p>
          <AnalysisReportView analysis={selectedReport.pose_data || {
            performance: { performance_score: selectedReport.performance_score, performance_level: selectedReport.performance_level },
            injury_risk: { risk_score: selectedReport.injury_risk_score, risk_level: selectedReport.risk_level, metrics: selectedReport.key_metrics || {} },
            pose_detection_rate: selectedReport.pose_detection_rate,
            analysis_confidence: selectedReport.analysis_confidence,
            recommendations: selectedReport.recommendations || []
          }} />
        </Card>
      </div>
    );
  }

  return (
    <Card title="Saved Analysis History">
      {loadingHistory ? (
        <p className="muted">Loading past reports...</p>
      ) : fetchError ? (
        <p className="muted" style={{ color: '#ef4444' }}>{fetchError}</p>
      ) : reports.length === 0 ? (
        <p className="muted">No saved video analyses found. Run a video analysis to store results here.</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {reports.map((report) => (
            <div
              key={report.id}
              onClick={() => setSelectedReport(report)}
              style={{
                display: 'flex',
                justify: 'space-between',
                alignItems: 'center',
                padding: '14px 18px',
                borderRadius: '8px',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                background: 'rgba(255, 255, 255, 0.03)',
                cursor: 'pointer',
                transition: 'border-color 0.2s'
              }}
              className="history-item"
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                <FileText size={20} style={{ color: '#10b981' }} />
                <div>
                  <b style={{ display: 'block', fontSize: '1rem' }}>{report.video_name}</b>
                  <span className="muted" style={{ fontSize: '0.85rem' }}>
                    {new Date(report.created_at).toLocaleDateString()} at{' '}
                    {new Date(report.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <div style={{ textAlign: 'right' }}>
                  <span style={{ display: 'block', fontSize: '0.85rem', color: '#10b981' }}>
                    Perf: <strong>{report.performance_score ?? '-'}</strong>/100 ({report.performance_level ?? 'N/A'})
                  </span>
                  <span style={{ display: 'block', fontSize: '0.85rem', color: '#ef4444' }}>
                    Risk: <strong>{report.injury_risk_score ?? '-'}</strong>/100 ({report.risk_level ?? 'N/A'})
                  </span>
                </div>

                <button
                  onClick={(e) => handleDelete(e, report.id)}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: '#ef4444',
                    cursor: 'pointer',
                    padding: '6px'
                  }}
                  title="Delete report"
                >
                  <Trash2 size={16} />
                </button>
                <ChevronRight size={18} className="muted" />
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}

/* --- Authentication Box Component --- */
function AuthForm({ onLoginSuccess }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSignUp, setIsSignUp] = useState(false);
  const [authError, setAuthError] = useState('');
  const [authLoading, setAuthLoading] = useState(false);

  const handleAuth = async (e) => {
    e.preventDefault();
    setAuthError('');
    setAuthLoading(true);

    try {
      if (isSignUp) {
        const { error } = await supabase.auth.signUp({ email, password });
        if (error) throw error;
        alert('Registration successful! Please log in.');
        setIsSignUp(false);
      } else {
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
        onLoginSuccess();
      }
    } catch (err) {
      setAuthError(err.message);
    } finally {
      setAuthLoading(false);
    }
  };

  return (
    <Card title={isSignUp ? 'Create SportAI Account' : 'Login to SportAI'}>
      <form onSubmit={handleAuth}>
        <input
          type="email"
          placeholder="Enter email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          style={{ width: '100%', marginBottom: '12px', padding: '10px' }}
        />
        <input
          type="password"
          placeholder="Enter password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          style={{ width: '100%', marginBottom: '16px', padding: '10px' }}
        />
        <button type="submit" className="primary" disabled={authLoading} style={{ width: '100%' }}>
          {authLoading ? 'Authenticating...' : isSignUp ? 'Sign Up' : 'Log In'}
        </button>
      </form>

      {authError && (
        <p className="muted" style={{ color: '#ef4444', marginTop: '10px' }}>
          {authError}
        </p>
      )}

      <p
        className="muted mt-15"
        style={{ cursor: 'pointer', color: '#10b981', textAlign: 'center' }}
        onClick={() => setIsSignUp(!isSignUp)}
      >
        {isSignUp ? 'Already have an account? Log In' : "Don't have an account? Sign Up"}
      </p>
    </Card>
  );
}

/* --- Main Dashboard Component --- */
function SportAIDashboard() {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard'); // 'dashboard' | 'analyze' | 'history'
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [analyzedVideoUrl, setAnalyzedVideoUrl] = useState(null);
  const [analyzedVideoName, setAnalyzedVideoName] = useState('');

  useEffect(() => () => {
    if (analyzedVideoUrl) URL.revokeObjectURL(analyzedVideoUrl);
  }, [analyzedVideoUrl]);

  useEffect(() => {
    supabase.auth.getUser().then(({ data: { user } }) => {
      setUser(user);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  const handleLogout = async () => {
    await supabase.auth.signOut();
    setUser(null);
    setResult(null);
    setAnalyzedVideoUrl(null);
    setAnalyzedVideoName('');
    setActiveTab('analyze');
  };

  const analyzeVideo = async () => {
    if (!file) {
      setError('Please select a video file first.');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE_URL}/api/analyze`, {
        method: 'POST',
        body: formData,
      });

      const responseText = await response.text();
      let data;
      try {
        data = responseText ? JSON.parse(responseText) : {};
      } catch {
        throw new Error(`Backend returned an invalid response (HTTP ${response.status}).`);
      }

      if (!response.ok) {
        throw new Error(`Analysis failed\nHTTP status: ${response.status}\nBackend detail: ${formatBackendDetail(data.detail)}`);
      }

      setResult(data);
      setAnalyzedVideoUrl((currentUrl) => {
        if (currentUrl) URL.revokeObjectURL(currentUrl);
        return URL.createObjectURL(file);
      });
      setAnalyzedVideoName(file.name);

      if (user) {
        const report = {
          user_id: user.id,
          analysis_id: data.analysis_id,
          video_id: data.file_id,
          video_name: file.name,
          sport: 'Cricket',
          activity: 'Video analysis',
          status: data.analysis?.status || 'analyzed',
          performance_score: data.analysis?.performance?.performance_score,
          performance_level: data.analysis?.performance?.performance_level,
          injury_risk_score: data.analysis?.injury_risk?.risk_score,
          risk_level: data.analysis?.injury_risk?.risk_level,
          pose_detection_rate: data.analysis?.pose_detection_rate,
          analysis_confidence: data.analysis?.analysis_confidence,
          analysis_quality: data.analysis?.analysis_quality,
          quality_level: data.analysis?.quality_level,
          quality_warnings: data.analysis?.quality_warnings || [],
          key_metrics: data.analysis?.injury_risk?.metrics || {},
          recommendations: data.analysis?.recommendations || [],
          pose_data: data.analysis
        };
        const { error: dbError } = await supabase.from('analysis_reports').insert([report]);
        if (dbError) {
          // The legacy fallback keeps existing deployments functional until the migration is applied.
          const { error: legacyError } = await supabase.from('analysis_reports').insert([{
            user_id: user.id, video_name: file.name,
            performance_score: report.performance_score, performance_level: report.performance_level,
            injury_risk_score: report.injury_risk_score, risk_level: report.risk_level,
            pose_data: report.pose_data
          }]);
          if (legacyError) {
            setError(`Analysis completed, but the report could not be saved: ${legacyError.message}`);
          }
        }
      }
    } catch (err) {
      console.error('Analysis error:', err);
      if (err instanceof TypeError) {
        setError(`Backend unavailable.\nMake sure FastAPI is running on: ${API_BASE_URL}`);
      } else {
        setError(err.message || 'Video analysis failed.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Header Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <section className="hero">
          <div className="eyebrow">
            <Sparkles size={16} />
            AI BIOMECHANICS & PERFORMANCE
          </div>
          <h1>SportAI Analytics Dashboard</h1>
        </section>

        {user && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span className="muted" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <UserCheck size={16} color="#10b981" /> {user.email}
            </span>
            <button className="outline" onClick={handleLogout} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <LogOut size={14} /> Logout
            </button>
          </div>
        )}
      </div>

      {!user ? (
        <div style={{ maxWidth: '480px', margin: '40px auto' }}>
          <AuthForm onLoginSuccess={() => console.log('Logged in successfully!')} />
        </div>
      ) : (
        <>
          {/* Navigation Tabs */}
          <div style={{ display: 'flex', gap: '10px', marginBottom: '20px', flexWrap: 'wrap' }}>
            <button
              className={activeTab === 'dashboard' ? 'primary' : 'outline'}
              onClick={() => setActiveTab('dashboard')}
              style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}
            >
              <BarChart3 size={16} /> PS-02 Dashboard
            </button>
            <button
              className={activeTab === 'analyze' ? 'primary' : 'outline'}
              onClick={() => setActiveTab('analyze')}
              style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}
            >
              <Upload size={16} /> Analyze Video
            </button>
            <button
              className={activeTab === 'history' ? 'primary' : 'outline'}
              onClick={() => setActiveTab('history')}
              style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}
            >
              <History size={16} /> Report History
            </button>
          </div>

          {activeTab === 'dashboard' ? (
            <PS02Dashboard analysis={result?.analysis} videoUrl={analyzedVideoUrl} videoName={analyzedVideoName} userId={user.id} onReanalyze={() => setActiveTab('analyze')} />
          ) : activeTab === 'history' ? (
            <HistoryView userId={user.id} />
          ) : (
            <>
              <section className="card">
                <h2>Upload Training Video</h2>
                <input
                  type="file"
                  accept="video/mp4,video/avi,video/mov,video/mkv"
                  onChange={(e) => setFile(e.target.files[0])}
                />

                {file && (
                  <p className="muted mt-8">
                    Selected: <strong>{file.name}</strong>
                  </p>
                )}

                <button
                  className="primary mt-15"
                  onClick={analyzeVideo}
                  disabled={loading}
                >
                  {loading ? 'Processing Frames...' : 'Analyze Video'}
                </button>

                {error && (
                  <div className="rec mt-15" style={{ background: 'rgba(239, 68, 68, 0.1)', borderColor: '#ef4444' }}>
                    <div className="rec-icon" style={{ background: 'rgba(239, 68, 68, 0.2)', color: '#ef4444' }}>
                      <AlertTriangle size={16} />
                    </div>
                    <div>
                      <b style={{ color: '#ef4444' }}>Error</b>
                      <span style={{ whiteSpace: 'pre-line' }}>{error}</span>
                    </div>
                  </div>
                )}
              </section>

              {result?.analysis && <><VideoSkeletonOverlay analysis={result.analysis} videoUrl={analyzedVideoUrl} videoName={analyzedVideoName} /><AnalysisReportView analysis={result.analysis} /></>}
            </>
          )}
        </>
      )}
    </div>
  );
}

const container = document.getElementById('root');
if (container) {
  const root = ReactDOM.createRoot(container);
  root.render(
    <React.StrictMode>
      <SportAIDashboard />
    </React.StrictMode>
  );
}
