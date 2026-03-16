import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const PPE_LABELS_VI = {
  helmet:          'Mũ bảo hộ',
  reflective_vest: 'Áo phản quang',
  gloves:          'Găng tay',
  safety_boots:    'Giày bảo hộ',
  safety_glasses:  'Kính bảo hộ',
};

export function ViolationChart({ data }) {
  // data có thể là array [{class_name, label, count}] hoặc object {helmet: 12, ...}
  let labels, values;
  if (Array.isArray(data)) {
    labels = data.map(d => d.label || PPE_LABELS_VI[d.class_name] || d.class_name);
    values = data.map(d => d.count);
  } else {
    labels = Object.keys(data).map(k => PPE_LABELS_VI[k] ?? k);
    values = Object.values(data);
  }

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Số lượt vi phạm',
        data: values,
        backgroundColor: 'rgba(239, 68, 68, 0.7)',
        borderColor: 'rgba(239, 68, 68, 1)',
        borderWidth: 1,
        borderRadius: 6,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { display: false },
      title: {
        display: true,
        text: 'Vi phạm theo loại trang bị bảo hộ',
        font: { size: 14 },
      },
    },
    scales: {
      y: { beginAtZero: true, ticks: { stepSize: 1 } },
    },
  };

  return (
    <div className="bg-white border rounded-lg p-4 shadow-sm mb-6">
      <Bar data={chartData} options={options} />
    </div>
  );
}
