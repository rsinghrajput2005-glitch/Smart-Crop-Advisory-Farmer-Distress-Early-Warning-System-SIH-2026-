import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Sprout, Home, CloudSun, BookOpen, Store, ShieldAlert, LayoutDashboard, Menu, X } from 'lucide-react';
import './Navbar.css';

const farmerLinks = [
  { to: '/', label: 'Home', icon: Home },
  { to: '/weather', label: 'Weather', icon: CloudSun },
  { to: '/advisory', label: 'Advisory', icon: BookOpen },
  { to: '/mandi', label: 'Mandi', icon: Store },
  { to: '/risk', label: 'Risk', icon: ShieldAlert },
];

const officerLinks = [
  { to: '/officer', label: 'Dashboard', icon: LayoutDashboard },
];

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();
  const isOfficer = location.pathname === '/officer';

  const links = isOfficer ? officerLinks : farmerLinks;

  return (
    <nav className="navbar">
      <Link to={isOfficer ? '/officer' : '/'} className="navbar-brand">
        <span className="brand-icon">
          <Sprout size={20} />
        </span>
        <span>KrishiRakshak</span>
        {isOfficer && <span className="officer-badge">Officer</span>}
      </Link>

      <button className="navbar-toggle" onClick={() => setMenuOpen(!menuOpen)}>
        {menuOpen ? <X size={22} /> : <Menu size={22} />}
      </button>

      <div className={`navbar-links ${menuOpen ? 'open' : ''}`}>
        {links.map((link) => {
          const Icon = link.icon;
          return (
            <Link
              key={link.to}
              to={link.to}
              className={`nav-link ${location.pathname === link.to ? 'active' : ''}`}
              onClick={() => setMenuOpen(false)}
            >
              <Icon size={16} />
              {link.label}
            </Link>
          );
        })}
        {!isOfficer && (
          <Link
            to="/officer"
            className={`nav-link ${location.pathname === '/officer' ? 'active' : ''}`}
            onClick={() => setMenuOpen(false)}
          >
            <LayoutDashboard size={16} />
            Officer
          </Link>
        )}
        {isOfficer && (
          <Link
            to="/"
            className="nav-link"
            onClick={() => setMenuOpen(false)}
          >
            <Home size={16} />
            Farmer View
          </Link>
        )}
      </div>
    </nav>
  );
}
