import { Phone, ShieldAlert, Ambulance, BriefcaseMedical } from 'lucide-react';

export default function EmergencyContacts() {
  const contacts = [
    { id: 1, name: 'Polícia Turística', number: '190', desc: 'Delegacia do Turista', icon: ShieldAlert, color: 'text-ocean', bg: 'bg-ocean/10' },
    { id: 2, name: 'SAMU (Urgência)', number: '192', desc: 'Ambulância Emergência', icon: Ambulance, color: 'text-coral', bg: 'bg-coral/10' },
    { id: 3, name: 'Hospitais / Clínicas', number: '193', desc: 'Bombeiros e Resgate', icon: BriefcaseMedical, color: 'text-yellow-500', bg: 'bg-yellow-50' },
  ];

  return (
    <div className="mb-8 pl-6 pr-6">
      <h2 className="text-xl font-bold text-gray-900 mb-4">Contatos Úteis</h2>
      <div className="flex flex-col gap-3">
        {contacts.map(contact => (
          <div key={contact.id} className="flex items-center p-4 bg-white rounded-[20px] shadow-sm border border-gray-100">
            <div className={`w-12 h-12 rounded-full ${contact.bg} flex items-center justify-center mr-4`}>
              <contact.icon className={`${contact.color} w-6 h-6`} />
            </div>
            <div className="flex-1">
              <h4 className="text-gray-900 font-bold text-sm">{contact.name}</h4>
              <p className="text-gray-500 text-xs">{contact.desc}</p>
            </div>
            <a href={`tel:${contact.number}`} className="w-10 h-10 rounded-full bg-gray-50 flex items-center justify-center hover:bg-gray-100 transition-colors">
              <Phone className="w-4 h-4 text-gray-700" />
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}
