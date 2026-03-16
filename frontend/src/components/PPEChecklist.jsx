const PPE_LABELS = {
  helmet:          { label: 'Mũ bảo hộ',     icon: '🪖' },
  reflective_vest: { label: 'Áo phản quang',  icon: '🦺' },
  gloves:          { label: 'Găng tay',        icon: '🧤' },
  safety_boots:    { label: 'Giày bảo hộ',    icon: '👟' },
  safety_glasses:  { label: 'Kính bảo hộ',    icon: '🥽' },
};

export function PPEChecklist({ items }) {
  const failEntries = Object.entries(items).filter(([, v]) => !v.detected);
  const failNames = failEntries.map(([k]) => PPE_LABELS[k]?.label ?? k);

  return (
    <div className="space-y-2">
      {Object.entries(items).map(([key, val]) => (
        <div
          key={key}
          className={`flex items-center justify-between px-3 py-2 rounded ${
            val.detected
              ? 'bg-green-50 text-green-700'
              : 'bg-red-50 text-red-700 font-semibold'
          }`}
        >
          <span>
            {val.detected ? '✅' : '❌'}{' '}
            {PPE_LABELS[key]?.icon} {PPE_LABELS[key]?.label ?? key}
          </span>
          <span className="text-sm">
            {val.detected
              ? `${Math.round(val.confidence * 100)}%`
              : 'Không phát hiện'}
          </span>
        </div>
      ))}
      {failEntries.length > 0 && (
        <div className="mt-3 text-red-600 text-sm font-medium">
          ⚠️ Thiếu {failEntries.length} hạng mục: {failNames.join(', ')}
        </div>
      )}
    </div>
  );
}
