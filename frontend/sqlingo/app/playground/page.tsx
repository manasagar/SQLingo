'use client';

import { useState } from 'react';
import { Press_Start_2P } from 'next/font/google';
import Link from 'next/link';
import { ArrowLeft, Database, Copy, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';

const pressStart2P = Press_Start_2P({
  weight: '400',
  subsets: ['latin']
});

interface ConnectionFormData {
  userId: string;
  link: string;
  username: string;
  password: string;
  database: string;
  type: string;
}

interface QueryResponse {
  created_at: string;
  res: string;
}

export default function Playground() {
  const [showConnectionDialog, setShowConnectionDialog] = useState(true);
  const [isConnecting, setIsConnecting] = useState(false);
  const [isQuerying, setIsQuerying] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);
  const [naturalLanguageQuery, setNaturalLanguageQuery] = useState('');
  const [sqlOutput, setSqlOutput] = useState('');
  const [formData, setFormData] = useState<ConnectionFormData>({
    userId: '',
    link: 'localhost:3308',
    username: '',
    password: '',
    database: '',
    type: 'mysql'
  });

  const handleConnect = async () => {
    // Validate all fields
    if (!formData.userId || !formData.username || !formData.password || !formData.database) {
      setError('All fields are required');
      return;
    }

    setIsConnecting(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/items', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Connection successful:', data);
        setShowConnectionDialog(false);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Connection failed. Please check your credentials.');
      }
    } catch (err) {
      setError('Error connecting to database. Please ensure the server is running.');
      console.error('Connection error:', err);
    } finally {
      setIsConnecting(false);
    }
  };

  const handleConvertToSQL = async () => {
    if (!naturalLanguageQuery.trim()) {
      setError('Please enter a query');
      return;
    }

    setIsQuerying(true);
    setError('');
    setSqlOutput('');

    try {
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId: formData.userId,
          query: naturalLanguageQuery
        }),
      });

      if (response.ok) {
        const data: QueryResponse = await response.json();
        setSqlOutput(data.res);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to convert query. Please try again.');
      }
    } catch (err) {
      setError('Error processing query. Please ensure the server is running.');
      console.error('Query error:', err);
    } finally {
      setIsQuerying(false);
    }
  };

  const handleCopySQL = async () => {
    if (!sqlOutput) return;

    try {
      await navigator.clipboard.writeText(sqlOutput);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const handleInputChange = (field: keyof ConnectionFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError(''); // Clear error when user types
  };

  if (showConnectionDialog) {
    return (
      <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
        <div className="bg-zinc-900 border-2 border-purple-500/50 rounded-lg shadow-2xl w-full max-w-md p-6 space-y-6">
          <div className="flex items-center gap-3 border-b border-zinc-700 pb-4">
            <Database className="w-8 h-8 text-purple-500" />
            <div>
              <h2 className={`${pressStart2P.className} text-xl text-white`}>
                Database Connection
              </h2>
              <p className="text-sm text-zinc-400 mt-1">
                Connect to your database to continue
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm text-zinc-300 mb-2" htmlFor="userId">
                User ID *
              </label>
              <input
                id="userId"
                type="text"
                value={formData.userId}
                onChange={(e) => handleInputChange('userId', e.target.value)}
                className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-md text-white focus:outline-none focus:border-purple-500 transition-colors"
                placeholder="manas"
              />
            </div>

            <div>
              <label className="block text-sm text-zinc-300 mb-2" htmlFor="type">
                Database Type *
              </label>
              <select
                id="type"
                value={formData.type}
                onChange={(e) => handleInputChange('type', e.target.value)}
                className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-md text-white focus:outline-none focus:border-purple-500 transition-colors"
              >
                <option value="mysql">MySQL</option>
                <option value="postgresql">PostgreSQL</option>
                <option value="sqlite">SQLite</option>
              </select>
            </div>

            <div>
              <label className="block text-sm text-zinc-300 mb-2" htmlFor="link">
                Database Host *
              </label>
              <input
                id="link"
                type="text"
                value={formData.link}
                onChange={(e) => handleInputChange('link', e.target.value)}
                className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-md text-white focus:outline-none focus:border-purple-500 transition-colors"
                placeholder="localhost:3308"
              />
            </div>

            <div>
              <label className="block text-sm text-zinc-300 mb-2" htmlFor="username">
                Username *
              </label>
              <input
                id="username"
                type="text"
                value={formData.username}
                onChange={(e) => handleInputChange('username', e.target.value)}
                className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-md text-white focus:outline-none focus:border-purple-500 transition-colors"
                placeholder="root"
              />
            </div>

            <div>
              <label className="block text-sm text-zinc-300 mb-2" htmlFor="password">
                Password *
              </label>
              <input
                id="password"
                type="password"
                value={formData.password}
                onChange={(e) => handleInputChange('password', e.target.value)}
                className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-md text-white focus:outline-none focus:border-purple-500 transition-colors"
                placeholder="••••••"
              />
            </div>

            <div>
              <label className="block text-sm text-zinc-300 mb-2" htmlFor="database">
                Database Name *
              </label>
              <input
                id="database"
                type="text"
                value={formData.database}
                onChange={(e) => handleInputChange('database', e.target.value)}
                className="w-full px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-md text-white focus:outline-none focus:border-purple-500 transition-colors"
                placeholder="llm"
              />
            </div>
          </div>

          {error && (
            <div className="p-3 bg-red-500/10 border border-red-500/50 rounded-md">
              <p className="text-sm text-red-400">{error}</p>
            </div>
          )}

          <Button
            onClick={handleConnect}
            disabled={isConnecting}
            className={`${pressStart2P.className} w-full bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed py-6`}
          >
            {isConnecting ? 'Connecting...' : 'Connect to Database'}
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <Link href="/">
            <Button
              variant="ghost"
              className={`${pressStart2P.className} text-white/80 hover:text-white`}
            >
              <ArrowLeft className="mr-2 w-4 h-4" />
              Back
            </Button>
          </Link>
          <h1 className={`${pressStart2P.className} text-2xl md:text-4xl text-white/80`}>
            Playground
          </h1>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/50 rounded-lg">
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Input Section */}
          <div className="space-y-4">
            <h2 className={`${pressStart2P.className} text-lg text-white/70`}>
              Natural Language Query
            </h2>
            <textarea
              value={naturalLanguageQuery}
              onChange={(e) => setNaturalLanguageQuery(e.target.value)}
              className="w-full h-64 p-4 bg-zinc-900 border border-zinc-700 rounded-lg text-white resize-none focus:outline-none focus:border-purple-500 transition-colors"
              placeholder="Enter your query in natural language...&#10;e.g., how many students in school"
            />
            <Button
              onClick={handleConvertToSQL}
              disabled={isQuerying || !naturalLanguageQuery.trim()}
              className={`${pressStart2P.className} w-full bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              {isQuerying ? 'Converting...' : 'Convert to SQL'}
            </Button>
          </div>

          {/* Output Section */}
          <div className="space-y-4">
            <h2 className={`${pressStart2P.className} text-lg text-white/70`}>
              SQL Query
            </h2>
            <div className="w-full h-64 p-4 bg-zinc-900 border border-zinc-700 rounded-lg text-green-400 font-mono overflow-auto whitespace-pre-wrap">
              {sqlOutput || '// SQL output will appear here...'}
            </div>
            <Button
              onClick={handleCopySQL}
              variant="outline"
              disabled={!sqlOutput}
              className={`${pressStart2P.className} w-full disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              {copied ? (
                <>
                  <Check className="mr-2 w-4 h-4" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="mr-2 w-4 h-4" />
                  Copy SQL
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}