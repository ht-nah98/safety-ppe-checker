export function ErrorMessage({ error, onRetry }) {
  return (
    <div className="bg-red-50 border border-red-300 rounded p-4">
      <p className="text-red-700">⚠️ {error}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-2 px-3 py-1 bg-red-100 hover:bg-red-200 text-red-700 rounded text-sm"
        >
          Thử lại
        </button>
      )}
    </div>
  );
}
