import { QRCodeSVG } from 'qrcode.react';
import { X, Share2, Copy } from 'lucide-react';

interface QrShareModalProps {
  isOpen: boolean;
  onClose: () => void;
  url: string;
}

export default function QrShareModal({ isOpen, onClose, url }: QrShareModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center pointer-events-auto">
      <div 
        className="absolute inset-0 bg-gray-900/40 backdrop-blur-sm" 
        onClick={onClose}
      />
      <div 
        className="relative bg-white w-full sm:w-auto min-w-[320px] rounded-t-[32px] sm:rounded-[32px] p-8 flex flex-col items-center animate-slide-up shadow-2xl"
      >
        <button 
          onClick={onClose}
          className="absolute top-6 right-6 w-8 h-8 flex items-center justify-center rounded-full bg-gray-100 text-gray-500 hover:bg-gray-200 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
        
        <div className="w-16 h-16 bg-ocean/10 rounded-full flex items-center justify-center mb-4">
          <Share2 className="w-8 h-8 text-ocean" />
        </div>
        
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Compartilhar Roteiro</h2>
        <p className="text-gray-500 text-center text-sm mb-8 max-w-[240px]">
          Mostre este código para seus amigos para sincronizar as atividades da viagem.
        </p>

        <div className="p-4 bg-white border-2 border-gray-100 rounded-2xl shadow-sm mb-6">
          <QRCodeSVG value={url} size={200} level="H" />
        </div>
        
        <div className="flex w-full gap-3">
          <button 
             onClick={() => navigator.clipboard.writeText(url)}
             className="flex-1 bg-gray-50 text-gray-700 py-3.5 rounded-2xl font-bold text-sm flex justify-center items-center gap-2 hover:bg-gray-100 transition-colors">
            <Copy className="w-4 h-4" />
            Copiar Link
          </button>
        </div>
      </div>
    </div>
  );
}
