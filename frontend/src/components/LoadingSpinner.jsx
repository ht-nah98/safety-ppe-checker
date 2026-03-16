export function LoadingSpinner({ message = 'AI đang phân tích... (~2-3 giây)' }) {
  return (
    <div className="flex flex-col items-center py-16">
      <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600" />
      <p className="mt-4 text-gray-600">{message}</p>
    </div>
  );
}
