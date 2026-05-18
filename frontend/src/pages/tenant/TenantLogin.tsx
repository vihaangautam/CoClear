import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Phone, ArrowRight, ShieldCheck } from 'lucide-react';
import { fetchApi } from '../../api';
import './TenantLogin.css';

export default function TenantLogin() {
  const [phone, setPhone] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (!phone || phone.length < 10) {
      setError('Enter a valid 10-digit phone number');
      return;
    }
    setLoading(true);
    try {
      const data: any = await fetchApi(`/tenant/lookup?phone=${encodeURIComponent(phone)}`);
      // Store tenant info in sessionStorage for the tenant portal
      sessionStorage.setItem('tenant_id', data.tenant.id);
      sessionStorage.setItem('tenant_name', data.tenant.name);
      sessionStorage.setItem('tenant_phone', data.tenant.phone);
      sessionStorage.setItem('tenant_tenancies', JSON.stringify(data.tenancies));
      navigate('/tenant/home');
    } catch (err: any) {
      if (err.message.includes('404')) {
        setError('No account found with this number. Please check with your PG owner.');
      } else {
        setError('Something went wrong. Try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="tenant-login-page">
      <div className="login-container">
        <div className="login-brand">
          <div className="login-logo">
            <ShieldCheck size={32} />
          </div>
          <h1>PGPal</h1>
          <p className="login-tagline">Your PG, your rights, your proof.</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <label className="login-label">Enter your registered phone number</label>
          <div className="phone-input-group">
            <div className="phone-prefix">
              <Phone size={18} />
              <span>+91</span>
            </div>
            <input
              type="tel"
              maxLength={10}
              placeholder="9876543210"
              value={phone}
              onChange={(e) => setPhone(e.target.value.replace(/\D/g, ''))}
              autoFocus
            />
          </div>

          {error && <p className="login-error">{error}</p>}

          <button type="submit" className="login-btn" disabled={loading}>
            {loading ? 'Finding your account...' : (
              <>Continue <ArrowRight size={18} /></>
            )}
          </button>
        </form>

        <p className="login-footer">
          Your PG owner added you to PGPal. This is where you'll find your room check reports,
          raise complaints, and track your deposit.
        </p>
      </div>
    </div>
  );
}
