import { useNavigate } from 'react-router-dom';

const PPE_LABELS_VI = {
  helmet:          'Mũ bảo hộ',
  reflective_vest: 'Áo phản quang',
  gloves:          'Găng tay',
  safety_boots:    'Giày bảo hộ',
  safety_glasses:  'Kính bảo hộ',
};

function formatDate(isoString) {
  return new Date(isoString).toLocaleString('vi-VN');
}

function getViolatedItems(insp) {
  // Ưu tiên violated_items nếu có, fallback tính từ items
  if (insp.violated_items) return insp.violated_items;
  if (insp.items) {
    return Object.entries(insp.items)
      .filter(([, v]) => !v.detected)
      .map(([k]) => k);
  }
  return [];
}

export function InspectionTable({ inspections, total, page, onPageChange, hidePagination = false }) {
  const navigate = useNavigate();
  const pageSize = 20;
  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="bg-white border rounded-lg shadow-sm overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-gray-50 border-b">
          <tr>
            <th className="text-left px-4 py-3 text-gray-600 font-medium">Thời gian</th>
            <th className="text-left px-4 py-3 text-gray-600 font-medium">Kết quả</th>
            <th className="text-left px-4 py-3 text-gray-600 font-medium">Vi phạm</th>
            <th className="text-right px-4 py-3 text-gray-600 font-medium">Chi tiết</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {inspections.map(insp => {
            const violated = getViolatedItems(insp);
            return (
              <tr key={insp.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 text-gray-700">{formatDate(insp.created_at)}</td>
                <td className="px-4 py-3">
                  <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-semibold ${
                    insp.overall_pass
                      ? 'bg-green-100 text-green-700'
                      : 'bg-red-100 text-red-700'
                  }`}>
                    {insp.overall_pass ? 'PASS' : 'FAIL'}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-500">
                  {violated.length === 0
                    ? <span className="text-green-600">—</span>
                    : violated.map(k => PPE_LABELS_VI[k] ?? k).join(', ')}
                </td>
                <td className="px-4 py-3 text-right">
                  <button
                    onClick={() => navigate(`/history/${insp.id}`)}
                    className="text-blue-600 hover:text-blue-800 hover:underline text-sm"
                  >
                    Xem
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>

      {!hidePagination && totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-3 border-t bg-gray-50">
          <span className="text-sm text-gray-500">
            Trang {page + 1} / {totalPages} — {total} bản ghi
          </span>
          <div className="flex gap-2">
            <button
              disabled={page === 0}
              onClick={() => onPageChange(page - 1)}
              className="px-3 py-1 border rounded text-sm disabled:opacity-40 hover:bg-gray-100"
            >
              ← Trước
            </button>
            <button
              disabled={page >= totalPages - 1}
              onClick={() => onPageChange(page + 1)}
              className="px-3 py-1 border rounded text-sm disabled:opacity-40 hover:bg-gray-100"
            >
              Sau →
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
