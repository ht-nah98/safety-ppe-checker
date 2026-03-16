export function StatsCards({ stats }) {
  // Backend trả về pass_rate là % (83.3), không phải ratio (0.833)
  const passRate = typeof stats.pass_rate === 'number'
    ? stats.pass_rate.toFixed(1)
    : (stats.compliance_rate * 100).toFixed(1);

  const total = stats.total_inspections ?? stats.total ?? 0;

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div className="bg-white border rounded-lg p-4 text-center shadow-sm">
        <div className="text-3xl font-bold text-gray-800">{total}</div>
        <div className="text-sm text-gray-500 mt-1">Tổng lượt kiểm tra</div>
      </div>
      <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center shadow-sm">
        <div className="text-3xl font-bold text-green-700">{stats.pass_count}</div>
        <div className="text-sm text-green-600 mt-1">PASS</div>
      </div>
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center shadow-sm">
        <div className="text-3xl font-bold text-red-700">{stats.fail_count}</div>
        <div className="text-sm text-red-600 mt-1">FAIL</div>
      </div>
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center shadow-sm">
        <div className="text-3xl font-bold text-blue-700">{passRate}%</div>
        <div className="text-sm text-blue-600 mt-1">Tỉ lệ đạt</div>
      </div>
    </div>
  );
}
