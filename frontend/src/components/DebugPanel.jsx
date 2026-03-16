import { useState } from 'react';

const CONF_THRESHOLDS = {
  helmet: 0.50,
  reflective_vest: 0.50,
  gloves: 0.40,
  safety_boots: 0.45,
  safety_glasses: 0.40,
};

function ConfBar({ value, threshold, max = 1.0 }) {
  const pct = Math.round(value * 100);
  const threshPct = Math.round((threshold ?? 0) * 100);
  const passed = value >= (threshold ?? 0);
  return (
    <div className="relative w-full h-4 bg-gray-100 rounded overflow-hidden">
      <div
        className={`h-full rounded transition-all ${passed ? 'bg-green-400' : 'bg-red-400'}`}
        style={{ width: `${Math.min(pct, 100)}%` }}
      />
      {threshold != null && (
        <div
          className="absolute top-0 bottom-0 w-0.5 bg-gray-700 opacity-60"
          style={{ left: `${threshPct}%` }}
          title={`Threshold: ${threshPct}%`}
        />
      )}
      <span className="absolute right-1 top-0 text-xs leading-4 text-gray-700 font-mono">
        {pct}%
      </span>
    </div>
  );
}

export function DebugPanel({ debugInfo, items }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="mt-4 border border-gray-200 rounded-lg overflow-hidden text-sm">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-4 py-2 bg-gray-50 hover:bg-gray-100 text-gray-600 font-mono"
      >
        <span>🔍 Debug — Chi tiết detection</span>
        <span>{open ? '▲' : '▼'}</span>
      </button>

      {open && (
        <div className="p-4 space-y-4 bg-white font-mono text-xs">

          {/* Model info */}
          {debugInfo && (
            <div className="bg-gray-50 rounded p-3 space-y-1">
              <div className="font-semibold text-gray-700 mb-1">📦 Model</div>
              <div>Path: <span className="text-blue-700">{debugInfo.model_path}</span></div>
              <div>Pre-filter conf: <span className="text-orange-600">{(debugInfo.inference_conf_threshold * 100).toFixed(0)}%</span></div>
              <div>Image size: <span className="text-gray-600">{debugInfo.image_size?.[1]}×{debugInfo.image_size?.[0]}px</span></div>
              <div>Raw detections (before threshold): <span className="font-bold">{debugInfo.raw_detection_count}</span></div>
            </div>
          )}

          {/* PPE class thresholds + result */}
          <div>
            <div className="font-semibold text-gray-700 mb-2">✅ Kết quả sau threshold filter</div>
            <div className="space-y-2">
              {Object.entries(items).map(([cls, val]) => (
                <div key={cls} className="flex items-center gap-2">
                  <span className="w-32 shrink-0 text-gray-600">{cls}</span>
                  <div className="flex-1">
                    <ConfBar
                      value={val.confidence}
                      threshold={CONF_THRESHOLDS[cls]}
                    />
                  </div>
                  <span className={`w-20 text-right shrink-0 ${val.detected ? 'text-green-600' : 'text-red-600'}`}>
                    {val.detected ? `✅ ${(val.confidence * 100).toFixed(0)}%` : '❌ miss'}
                  </span>
                </div>
              ))}
            </div>
            <div className="text-gray-400 mt-1">▏ = ngưỡng confidence tối thiểu</div>
          </div>

          {/* Raw detections table */}
          {debugInfo?.raw_detections?.length > 0 && (
            <div>
              <div className="font-semibold text-gray-700 mb-2">
                📋 Raw detections từ YOLO ({debugInfo.raw_detections.length} boxes)
              </div>
              <table className="w-full border-collapse">
                <thead>
                  <tr className="bg-gray-100 text-gray-600">
                    <th className="text-left px-2 py-1 border">YOLO class</th>
                    <th className="text-left px-2 py-1 border">→ PPE class</th>
                    <th className="text-right px-2 py-1 border">Conf</th>
                    <th className="text-right px-2 py-1 border">Threshold</th>
                    <th className="text-center px-2 py-1 border">Pass?</th>
                  </tr>
                </thead>
                <tbody>
                  {debugInfo.raw_detections.map((d, i) => (
                    <tr key={i} className={d.passed_threshold ? 'bg-green-50' : d.ppe_class ? 'bg-yellow-50' : 'bg-gray-50'}>
                      <td className="px-2 py-1 border text-blue-700">{d.raw_class}</td>
                      <td className="px-2 py-1 border text-purple-700">{d.ppe_class ?? <span className="text-gray-400">— ignored</span>}</td>
                      <td className="px-2 py-1 border text-right">{(d.confidence * 100).toFixed(1)}%</td>
                      <td className="px-2 py-1 border text-right text-orange-600">
                        {d.threshold != null ? `${(d.threshold * 100).toFixed(0)}%` : '—'}
                      </td>
                      <td className="px-2 py-1 border text-center">
                        {d.ppe_class == null ? '⊘' : d.passed_threshold ? '✅' : '❌'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {debugInfo?.raw_detection_count === 0 && (
            <div className="bg-yellow-50 border border-yellow-300 rounded p-3 text-yellow-800">
              ⚠️ YOLO không detect được object nào trong ảnh này.<br />
              Nguyên nhân có thể: model chưa được train cho PPE (đang dùng COCO pretrained),
              hoặc ảnh không rõ ràng.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
