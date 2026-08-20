'use client';

import { useState, useEffect, useCallback } from 'react';
import { Signal, NewsEvent, MarketStatus } from '@/types';
import SignalCard from '@/components/SignalCard';
import SignalDetail from '@/components/SignalDetail';
import NewsCalendar from '@/components/NewsCalendar';
import MarketStatusBar from '@/components/MarketStatusBar';
import { RefreshCw, Filter, Zap, Search, Plus, X } from 'lucide-react';

const DEFAULT_SYMBOLS = ['AAPL', 'MSFT', 'TSLA', 'NVDA', 'AMZN', 'GOOGL', 'META', 'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'BTC-USD', 'ETH-USD'];

const SYMBOL_LABELS: Record<string, string> = {
  'AAPL': 'Apple',
  'MSFT': 'Microsoft',
  'TSLA': 'Tesla',
  'NVDA': 'NVIDIA',
  'AMZN': 'Amazon',
  'GOOGL': 'Alphabet',
  'META': 'Meta',
  'EURUSD=X': 'EUR/USD',
  'GBPUSD=X': 'GBP/USD',
  'USDJPY=X': 'USD/JPY',
  'AUDUSD=X': 'AUD/USD',
  'USDCHF=X': 'USD/CHF',
  'USDCAD=X': 'USD/CAD',
  'NZDUSD=X': 'NZD/USD',
  'BTC-USD': 'Bitcoin',
  'ETH-USD': 'Ethereum',
};

export default function Home() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [allSignals, setAllSignals] = useState<Signal[]>([]);
  const [news, setNews] = useState<NewsEvent[]>([]);
  const [marketStatus, setMarketStatus] = useState<MarketStatus | null>(null);
  const [warnings, setWarnings] = useState<string[]>([]);
  const [selectedSignal, setSelectedSignal] = useState<Signal | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'buy' | 'sell'>('all');
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [customSymbol, setCustomSymbol] = useState('');
  const [selectedSymbols, setSelectedSymbols] = useState<string[]>(DEFAULT_SYMBOLS);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async (symbols?: string[]) => {
    try {
      setLoading(true);
      setError(null);
      
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://trading-signals-a356.onrender.com';
      const symbolsToFetch = symbols || selectedSymbols;
      const symbolsParam = symbolsToFetch.join(',');
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 120000);
      
      const signalsRes = await fetch(`${API_URL}/api/signals?symbols=${symbolsParam}`, {
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      
      if (!signalsRes.ok) {
        throw new Error(`API returned ${signalsRes.status}`);
      }
      
      const signalsData = await signalsRes.json();
      
      setSignals(signalsData.signals || []);
      setAllSignals(signalsData.all_signals || []);
      
      const newsRes = await fetch(`${API_URL}/api/news`, { signal: controller.signal });
      const newsData = await newsRes.json();
      setNews(newsData.upcoming_events || []);
      setWarnings(newsData.current_status?.warnings || []);
      
      const statusRes = await fetch(`${API_URL}/api/market-status`, { signal: controller.signal });
      const statusData = await statusRes.json();
      setMarketStatus(statusData.market);
      
      setLastUpdate(new Date());
    } catch (error: any) {
      console.error('Error fetching data:', error);
      if (error.name === 'AbortError') {
        setError('Backend is waking up from sleep. Please wait and try again in 30 seconds.');
      } else {
        setError('Failed to fetch signals. The backend may be waking up - try refreshing.');
      }
    } finally {
      setLoading(false);
    }
  }, [selectedSymbols]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(() => fetchData(), 60000);
    
    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://trading-signals-a356.onrender.com';
    const keepAlive = setInterval(() => {
      fetch(`${API_URL}/api/ping`).catch(() => {});
    }, 300000);
    
    return () => {
      clearInterval(interval);
      clearInterval(keepAlive);
    };
  }, [fetchData]);

  const addSymbol = () => {
    const symbol = customSymbol.trim().toUpperCase();
    if (!symbol) return;
    
    const formatted = symbol.endsWith('=X') ? symbol : symbol;
    if (!selectedSymbols.includes(formatted)) {
      const updated = [...selectedSymbols, formatted];
      setSelectedSymbols(updated);
      fetchData(updated);
    }
    setCustomSymbol('');
  };

  const removeSymbol = (symbol: string) => {
    const updated = selectedSymbols.filter(s => s !== symbol);
    setSelectedSymbols(updated);
    fetchData(updated);
  };

  const addPreset = (symbol: string) => {
    if (!selectedSymbols.includes(symbol)) {
      const updated = [...selectedSymbols, symbol];
      setSelectedSymbols(updated);
      fetchData(updated);
    }
  };

  const filteredSignals = allSignals.filter((signal) => {
    const matchesFilter = filter === 'all' ||
      (filter === 'buy' && signal.signal_type.includes('BUY')) ||
      (filter === 'sell' && signal.signal_type.includes('SELL'));
    
    const matchesSearch = !searchQuery ||
      signal.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (SYMBOL_LABELS[signal.symbol] || '').toLowerCase().includes(searchQuery.toLowerCase());
    
    return matchesFilter && matchesSearch;
  });

  const strongSignals = allSignals.filter(s => s.signal_type !== 'NEUTRAL');

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Trading Signals Dashboard
              </h1>
              <p className="text-gray-500 mt-1">
                Real-time forex and stock signals with technical analysis
              </p>
            </div>
            <div className="flex items-center gap-4">
              {lastUpdate && (
                <p className="text-sm text-gray-400">
                  Updated: {lastUpdate.toLocaleTimeString()}
                </p>
              )}
              <button
                onClick={() => fetchData()}
                disabled={loading}
                className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </button>
            </div>
          </div>
        </div>

        {marketStatus && <MarketStatusBar status={marketStatus} />}

        {warnings.length > 0 && (
          <div className="mt-6 p-4 bg-red-50 rounded-xl border border-red-200">
            <div className="flex items-center gap-2 mb-2">
              <Zap className="w-5 h-5 text-red-500" />
              <h3 className="font-semibold text-red-800">High Impact News Warning</h3>
            </div>
            <ul className="space-y-1">
              {warnings.map((warning, idx) => (
                <li key={idx} className="text-sm text-red-700">• {warning}</li>
              ))}
            </ul>
          </div>
        )}

        {error && (
          <div className="mt-6 p-4 bg-yellow-50 rounded-xl border border-yellow-200">
            <div className="flex items-center gap-2">
              <Zap className="w-5 h-5 text-yellow-500" />
              <p className="text-sm text-yellow-800">{error}</p>
            </div>
            <button
              onClick={() => { setError(null); fetchData(); }}
              className="mt-2 text-sm font-medium text-yellow-700 hover:text-yellow-900 underline"
            >
              Try again
            </button>
          </div>
        )}

        {/* Search and Symbol Management */}
        <div className="mt-6 bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <div className="flex items-center gap-2 mb-4">
            <Search className="w-5 h-5 text-gray-400" />
            <h2 className="text-lg font-bold text-gray-900">Search & Manage Symbols</h2>
          </div>

          {/* Search Bar */}
          <div className="relative mb-4">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search signals... (e.g. AAPL, Bitcoin, EUR)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Add Custom Symbol */}
          <div className="flex gap-2 mb-4">
            <input
              type="text"
              placeholder="Add symbol (e.g. GOOGL, USDJPY=X, XRP-USD)"
              value={customSymbol}
              onChange={(e) => setCustomSymbol(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && addSymbol()}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            />
            <button
              onClick={addSymbol}
              className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition"
            >
              <Plus className="w-4 h-4" />
              Add
            </button>
          </div>

          {/* Preset Quick Add */}
          <div className="mb-4">
            <p className="text-xs text-gray-500 mb-2">Quick add:</p>
            <div className="flex flex-wrap gap-2">
              {['GOOGL', 'AMZN', 'META', 'AUDUSD=X', 'USDCAD=X', 'NZDUSD=X', 'ETH-USD'].map(symbol => (
                !selectedSymbols.includes(symbol) && (
                  <button
                    key={symbol}
                    onClick={() => addPreset(symbol)}
                    className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 px-2 py-1 rounded transition"
                  >
                    + {SYMBOL_LABELS[symbol] || symbol}
                  </button>
                )
              ))}
            </div>
          </div>

          {/* Active Symbols */}
          <div>
            <p className="text-xs text-gray-500 mb-2">Tracking ({selectedSymbols.length}):</p>
            <div className="flex flex-wrap gap-2">
              {selectedSymbols.map(symbol => (
                <span
                  key={symbol}
                  className="inline-flex items-center gap-1 bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full"
                >
                  {SYMBOL_LABELS[symbol] || symbol}
                  <button
                    onClick={() => removeSymbol(symbol)}
                    className="hover:text-red-600 transition"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Signals Grid */}
        <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Filter className="w-5 h-5 text-gray-400" />
                <h2 className="text-lg font-bold text-gray-900">Signals</h2>
                <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded-full">
                  {filteredSignals.length} results
                </span>
                {strongSignals.length > 0 && (
                  <span className="bg-green-100 text-green-800 text-xs font-medium px-2 py-1 rounded-full">
                    {strongSignals.length} actionable
                  </span>
                )}
              </div>
              <div className="flex gap-2">
                {(['all', 'buy', 'sell'] as const).map(f => (
                  <button
                    key={f}
                    onClick={() => setFilter(f)}
                    className={`px-3 py-1 rounded-lg text-sm font-medium transition ${
                      filter === f
                        ? f === 'all' ? 'bg-gray-900 text-white'
                          : f === 'buy' ? 'bg-green-600 text-white'
                          : 'bg-red-600 text-white'
                        : f === 'all' ? 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                        : f === 'buy' ? 'bg-green-100 text-green-600 hover:bg-green-200'
                        : 'bg-red-100 text-red-600 hover:bg-red-200'
                    }`}
                  >
                    {f.charAt(0).toUpperCase() + f.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[1, 2, 3, 4].map(i => (
                  <div key={i} className="bg-white rounded-xl shadow-lg p-6 animate-pulse">
                    <div className="h-4 bg-gray-200 rounded w-1/3 mb-4" />
                    <div className="h-8 bg-gray-200 rounded w-1/2 mb-4" />
                    <div className="space-y-2">
                      <div className="h-3 bg-gray-200 rounded" />
                      <div className="h-3 bg-gray-200 rounded w-5/6" />
                    </div>
                  </div>
                ))}
              </div>
            ) : filteredSignals.length === 0 ? (
              <div className="bg-white rounded-xl shadow-lg p-12 text-center">
                <Search className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 text-lg">
                  {searchQuery ? `No signals found for "${searchQuery}"` : 'No signals found'}
                </p>
                <p className="text-gray-400 text-sm mt-2">
                  Try adding symbols or adjusting your search
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {filteredSignals.map((signal, idx) => (
                  <SignalCard
                    key={`${signal.symbol}-${idx}`}
                    signal={signal}
                    onClick={() => setSelectedSignal(signal)}
                  />
                ))}
              </div>
            )}
          </div>

          <div className="lg:col-span-1">
            <NewsCalendar events={news} currentWarnings={warnings} />
          </div>
        </div>

        {selectedSignal && (
          <SignalDetail signal={selectedSignal} onClose={() => setSelectedSignal(null)} />
        )}
      </div>
    </main>
  );
}
