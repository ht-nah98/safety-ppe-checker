export function VerdictHeader({ overallPass, timestamp }) {
  return (
    <div className={`border-l-4 rounded p-4 mb-6 ${
      overallPass
        ? 'bg-green-50 border-green-500 text-green-800'
        : 'bg-red-50 border-red-500 text-red-800'
    }`}>
      <span className="text-2xl font-bold">
        {overallPass
          ? '✅ PASS — ĐỦ TRANG BỊ BẢO HỘ'
          : '❌ FAIL — THIẾU TRANG BỊ BẢO HỘ'}
      </span>
      {timestamp && (
        <p className="text-sm mt-1 opacity-75">{timestamp}</p>
      )}
    </div>
  );
}
