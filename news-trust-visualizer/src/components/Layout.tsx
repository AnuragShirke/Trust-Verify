
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { cn } from '../lib/utils';
import { ThemeToggle } from './ThemeToggle';
import { Button } from './ui/button';
import { Avatar, AvatarFallback } from './ui/avatar';
import { useAuth } from '../context/AuthContext';

const navItems = [
  { name: 'Home', path: '/' },
  { name: 'About', path: '/about' },
  { name: 'FAQ', path: '/faq' },
  { name: 'History', path: '/history' },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const { user, isAuthenticated, logout } = useAuth();

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(part => part[0])
      .join('')
      .toUpperCase();
  };

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white dark:bg-gray-900 shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <Link to="/" className="flex items-center space-x-2">
              <span className="bg-primary rounded-full p-2">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5 text-primary-foreground">
                  <path d="M12 16c.5 0 .9-.1 1.1-.3.3-.2.4-.5.4-1 0-.4-.1-.7-.4-.9-.3-.2-.6-.3-1.1-.3-.5 0-.9.1-1.1.3-.3.2-.4.5-.4.9 0 .5.1.8.4 1 .3.2.6.3 1.1.3Z"></path>
                  <path d="M20.1 7c.7-1.7.7-3.7.3-4.3-.4-.5-2.5-.5-4.3.3-1.8.8-3.3.8-4.6.2-1.8-.8-3.9-.8-4.4-.3-.4.5-.1 2.6.9 4.3 1 1.7.9 3.4-.1 4.8-1 1.4-1.1 3.2-.3 4.7.7 1.5 2.7 1.8 5.1.4 2.4-1.4 5.4-1.4 7.8 0 2.4 1.3 4.2.9 4.8-.6.6-1.5-.1-3.8-1.7-5.2-1.6-1.4-2.1-3.1-1.7-4.6"></path>
                </svg>
              </span>
              <span className="font-semibold text-xl text-gray-900 dark:text-white">TrustVerify</span>
            </Link>

            <nav className="hidden md:flex space-x-8 items-center">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={cn(
                    "text-sm font-medium transition-colors px-2 py-1 rounded-md",
                    location.pathname === item.path
                      ? "text-primary border-b-2 border-primary"
                      : "text-gray-600 dark:text-gray-300 hover:text-primary dark:hover:text-primary"
                  )}
                >
                  {item.name}
                </Link>
              ))}

              <div className="flex items-center space-x-4">
                {isAuthenticated ? (
                  <div className="flex items-center space-x-4">
                    <Link to="/profile" className="flex items-center space-x-2">
                      <Avatar className="h-8 w-8">
                        <AvatarFallback>{user ? getInitials(user.username || user.email) : 'U'}</AvatarFallback>
                      </Avatar>
                      <span className="text-sm font-medium">{user?.username}</span>
                    </Link>
                    <Button variant="ghost" size="sm" onClick={logout}>
                      Logout
                    </Button>
                  </div>
                ) : (
                  <div className="flex items-center space-x-2">
                    <Link to="/login">
                      <Button variant="ghost" size="sm">Login</Button>
                    </Link>
                    <Link to="/register">
                      <Button size="sm">Register</Button>
                    </Link>
                  </div>
                )}
                <ThemeToggle />
              </div>
            </nav>

            <div className="md:hidden flex items-center space-x-4">
              {isAuthenticated ? (
                <Link to="/profile">
                  <Avatar className="h-8 w-8">
                    <AvatarFallback>{user ? getInitials(user.username || user.email) : 'U'}</AvatarFallback>
                  </Avatar>
                </Link>
              ) : (
                <Link to="/login">
                  <Button size="sm">Login</Button>
                </Link>
              )}
              <ThemeToggle />
              <button
                type="button"
                className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white focus:outline-none"
              >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-grow container mx-auto px-4 py-8">
        {children}
      </main>

      <footer className="bg-gray-50 dark:bg-gray-800 border-t dark:border-gray-700">
        <div className="container mx-auto px-4 py-6">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              © {new Date().getFullYear()} TrustVerify. All rights reserved.
            </p>
            <div className="flex space-x-4 mt-4 md:mt-0">
              <a href="#" className="text-sm text-gray-600 dark:text-gray-400 hover:text-primary dark:hover:text-primary">
                Privacy Policy
              </a>
              <a href="#" className="text-sm text-gray-600 dark:text-gray-400 hover:text-primary dark:hover:text-primary">
                Terms of Service
              </a>
              <a href="#" className="text-sm text-gray-600 dark:text-gray-400 hover:text-primary dark:hover:text-primary">
                Contact
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
