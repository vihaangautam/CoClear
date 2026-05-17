import { useEffect, useState } from 'react';
import { Building2, Plus, MapPin } from 'lucide-react';
import { fetchApi } from '../api';
import './Pages.css';

interface Property {
  id: string; name: string; address: string; type: string; created_at: string;
}

export default function Properties() {
  const [properties, setProperties] = useState<Property[]>([]);
  useEffect(() => { fetchApi<Property[]>('/properties').then(setProperties); }, []);

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1 className="page-title">Properties</h1>
          <p className="page-subtitle">Manage your PG properties and rooms</p>
        </div>
        <button className="btn-primary"><Plus size={16} /> Add Property</button>
      </header>

      <div className="table-card card">
        <table className="data-table">
          <thead>
            <tr>
              <th>Property</th>
              <th>Address</th>
              <th>Type</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {properties.map((p) => (
              <tr key={p.id}>
                <td>
                  <div className="cell-with-icon">
                    <div className="cell-icon"><Building2 size={16} /></div>
                    <span className="cell-primary">{p.name}</span>
                  </div>
                </td>
                <td><div className="cell-with-icon small"><MapPin size={14} />{p.address}</div></td>
                <td><span className={`type-badge ${p.type}`}>{p.type}</span></td>
                <td className="mono-text">{new Date(p.created_at).toLocaleDateString('en-IN')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
