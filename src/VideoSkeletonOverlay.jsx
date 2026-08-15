import React, { useCallback, useEffect, useRef } from "react";

const JOINTS = [
  'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
  'left_wrist', 'right_wrist', 'left_hip', 'right_hip',
  'left_knee', 'right_knee', 'left_ankle', 'right_ankle'
];

const CONNECTIONS = [
  ['left_shoulder', 'right_shoulder'], ['left_shoulder', 'left_elbow'],
  ['left_elbow', 'left_wrist'], ['right_shoulder', 'right_elbow'],
  ['right_elbow', 'right_wrist'], ['left_shoulder', 'left_hip'],
  ['right_shoulder', 'right_hip'], ['left_hip', 'right_hip'],
  ['left_hip', 'left_knee'], ['left_knee', 'left_ankle'],
  ['right_hip', 'right_knee'], ['right_knee', 'right_ankle']
];

const RISK_COLORS = { normal: '#10b981', deviation: '#f59e0b', elevated: '#ef4444' };

function jointRisks(injuryRisk = {}) {
  const risks = Object.fromEntries(JOINTS.map((joint) => [joint, { level: 'normal', label: 'Normal movement' }]));
  const factors = injuryRisk.factors || [];

  const applyFactor = (pattern, joints, label) => {
    const factor = factors.find((item) => pattern.test(item));
    if (!factor) return;
    const level = /high|excessive/i.test(factor) ? 'elevated' : 'deviation';
    joints.forEach((joint) => { risks[joint] = { level, label }; });
  };

  applyFactor(/knee asymmetry/i, ['left_knee', 'right_knee'], 'Knee movement deviation');
  applyFactor(/hip asymmetry/i, ['left_hip', 'right_hip'], 'Hip movement deviation');
  applyFactor(/elbow asymmetry/i, ['left_elbow', 'right_elbow'], 'Elbow movement deviation');
  applyFactor(/shoulder asymmetry/i, ['left_shoulder', 'right_shoulder'], 'Shoulder movement deviation');
  return risks;
}

export default function VideoSkeletonOverlay({ analysis, videoUrl, videoName }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const frames = analysis?.frame_data || [];
  const risks = jointRisks(analysis?.injury_risk);

  const closestFrame = useCallback((timeSeconds) => {
    if (!frames.length) return null;
    let low = 0;
    let high = frames.length - 1;
    const target = timeSeconds * 1000;
    while (low < high) {
      const mid = Math.floor((low + high) / 2);
      if ((frames[mid].timestamp_ms ?? frames[mid].timestamp_seconds * 1000) < target) low = mid + 1;
      else high = mid;
    }
    const current = frames[low];
    const previous = frames[Math.max(0, low - 1)];
    const currentTime = current.timestamp_ms ?? current.timestamp_seconds * 1000;
    const previousTime = previous.timestamp_ms ?? previous.timestamp_seconds * 1000;
    return Math.abs(previousTime - target) < Math.abs(currentTime - target) ? previous : current;
  }, [frames]);

  const draw = useCallback(() => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;
    const rect = video.getBoundingClientRect();
    const ratio = window.devicePixelRatio || 1;
    const width = Math.round(rect.width * ratio);
    const height = Math.round(rect.height * ratio);
    if (canvas.width !== width || canvas.height !== height) {
      canvas.width = width;
      canvas.height = height;
    }
    const context = canvas.getContext('2d');
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    context.clearRect(0, 0, rect.width, rect.height);
    const frame = closestFrame(video.currentTime);
    if (!frame) return;
    const coordinate = (joint) => {
      const point = frame[joint];
      if (!point || point.visibility < 0.25) return null;
      return { x: point.x * rect.width, y: point.y * rect.height };
    };

    context.lineWidth = 3;
    context.lineCap = 'round';
    CONNECTIONS.forEach(([start, end]) => {
      const a = coordinate(start);
      const b = coordinate(end);
      if (!a || !b) return;
      context.strokeStyle = RISK_COLORS[risks[start].level] === RISK_COLORS[risks[end].level]
        ? RISK_COLORS[risks[start].level] : '#94a3b8';
      context.beginPath();
      context.moveTo(a.x, a.y);
      context.lineTo(b.x, b.y);
      context.stroke();
    });

    JOINTS.forEach((joint) => {
      const point = coordinate(joint);
      if (!point) return;
      const risk = risks[joint];
      context.fillStyle = RISK_COLORS[risk.level];
      context.beginPath();
      context.arc(point.x, point.y, 5, 0, Math.PI * 2);
      context.fill();
      if (risk.level !== 'normal') {
        context.font = '12px Inter, sans-serif';
        context.fillStyle = '#ffffff';
        context.fillText(risk.label, point.x + 8, point.y - 8);
      }
    });
  }, [closestFrame, risks]);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return undefined;
    const update = () => draw();
    const animate = () => { draw(); animationRef.current = requestAnimationFrame(animate); };
    const play = () => { animationRef.current = requestAnimationFrame(animate); };
    const stop = () => { cancelAnimationFrame(animationRef.current); draw(); };
    const resizeObserver = new ResizeObserver(draw);
    resizeObserver.observe(video);
    video.addEventListener('loadedmetadata', update);
    video.addEventListener('seeked', update);
    video.addEventListener('pause', stop);
    video.addEventListener('play', play);
    return () => {
      cancelAnimationFrame(animationRef.current);
      resizeObserver.disconnect();
      video.removeEventListener('loadedmetadata', update);
      video.removeEventListener('seeked', update);
      video.removeEventListener('pause', stop);
      video.removeEventListener('play', play);
    };
  }, [draw]);

  if (!videoUrl) return null;
  if (!frames.length) return <section className="card"><h2>Video Skeleton Overlay</h2><p className="muted">Pose overlay unavailable for this analysis.</p></section>;

  return (
    <section className="card video-overlay-card">
      <h2>Video Skeleton Overlay</h2>
      <p className="muted">{videoName} — synchronized with the analyzed MediaPipe pose data.</p>
      <div className="video-overlay-stage">
        <video ref={videoRef} className="analysis-video" controls preload="metadata" src={videoUrl} />
        <canvas ref={canvasRef} className="skeleton-overlay" aria-label="MediaPipe skeleton overlay" />
      </div>
      <p className="overlay-legend"><span className="legend-dot normal" /> Normal movement <span className="legend-dot deviation" /> Movement deviation <span className="legend-dot elevated" /> Elevated movement-risk indicator</p>
    </section>
  );
}
