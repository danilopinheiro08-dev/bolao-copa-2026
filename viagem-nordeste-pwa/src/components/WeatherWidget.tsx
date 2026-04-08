import { useState, useEffect } from 'react';
import { Sun, Droplets, ThermometerSun } from 'lucide-react';

export default function WeatherWidget() {
  const [data, setData] = useState({
    temp: 29,
    condition: 'Ensolarado',
    uvIndex: 'Muito Alto (10)',
    waterTemp: '28°C'
  });

  // Mocking an API call delay for realism
  useEffect(() => {
    const timer = setTimeout(() => {
      setData({
        temp: 30,
        condition: 'Céu Limpo',
        uvIndex: 'Extremo (11)',
        waterTemp: '28.5°C'
      });
    }, 1500);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="bg-white rounded-[24px] p-6 shadow-sm mb-6 border border-gray-100 flex flex-col gap-4">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-gray-500 text-sm font-medium mb-1">Clima Agora</h3>
          <div className="flex items-center gap-2">
            <span className="text-3xl font-bold text-gray-900">{data.temp}°</span>
            <div className="flex flex-col">
              <span className="text-sm font-medium text-gray-900">{data.condition}</span>
              <span className="text-xs text-gray-500">Natal, RN</span>
            </div>
          </div>
        </div>
        <div className="w-16 h-16 bg-yellow-50 rounded-full flex items-center justify-center">
          <Sun className="text-yellow-400 w-8 h-8" />
        </div>
      </div>
      
      <div className="flex gap-4 pt-4 border-t border-gray-50">
        <div className="flex items-center gap-2 flex-1">
          <ThermometerSun className="text-coral w-4 h-4" />
          <div className="flex flex-col">
            <span className="text-xs text-gray-500">Índice UV</span>
            <span className="text-sm font-medium text-gray-900">{data.uvIndex}</span>
          </div>
        </div>
        <div className="flex items-center gap-2 flex-1">
          <Droplets className="text-ocean w-4 h-4" />
          <div className="flex flex-col">
            <span className="text-xs text-gray-500">Temp. Água</span>
            <span className="text-sm font-medium text-gray-900">{data.waterTemp}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
