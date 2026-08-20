'use client';

import { useState, useEffect } from 'react';
import { Signal, NewsEvent, MarketStatus } from '@/types';
import SignalCard from '@/components/SignalCard';
import SignalDetail from '@/components/SignalDetail';
import NewsCalendar from '@/components/NewsCalendar';
import MarketStatusBar from '@/components/MarketStatusBar';
import { RefreshCw, Filter, Zap } from 'lucide-react';

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

  const fetchData = async () => {
    try {
      setLoading(true);
      
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://trading-signals-a356.onrender.com';
      
      const signalsRes = await fetch(`${API_URL}/api/signals?symbols=AAPL,MSFT,TSLA,NVDA,EURUSD=X,GBPUSD=X,BTC-USD`);
      const signalsData = await signalsRes.json();
      
      setSignals(signalsData.signals || []);
      setAllSignals(signalsData.all_signals || []);
      
      const newsRes = await fetch(`${API_URL}/api/news`);
      const newsData = await newsRes.json();
      setNews(newsData.upcoming_events || []);
      setWarnings(newsData.current_status?.warnings || []);
      
      const statusRes = await fetch(`${API_URL}/api/market-status`);
      const statusData = await statusRes.json();
      setMarketStatus(statusData.market);
      
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
  }, []);

  const filteredSignals = allSignals.filter((signal) => {
    if (filter === 'all') return true;
    if (filter === 'buy') return signal.signal_type.includes('BUY');
    if (filter === 'sell') return signal.signal_type.includes('SELL');
    return true;
  });

  const strongSignals = allSignals.filter(
    (s) => s.signal_type !== 'NEUTRAL'
  );

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
                  Last updated: {lastUpdate.toLocaleTimeString()}
                </p>
              )}
              <button
                onClick={fetchData}
                disabled={loading}
                className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
              >
                <RefreshCw
                  className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`}
                />
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
                <li key={idx} className="text-sm text-red-700">
                  • {warning}
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Filter className="w-5 h-5 text-gray-400" />
                <h2 className="text-lg font-bold text-gray-900">Active Signals</h2>
                <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded-full">
                  {strongSignals.length} actionable
                </span>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setFilter('all')}
                  className={`px-3 py-1 rounded-lg text-sm font-medium transition ${
                    filter === 'all'
                      ? 'bg-gray-900 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  All
                </button>
                <button
                  onClick={() => setFilter('buy')}
                  className={`px-3 py-1 rounded-lg text-sm font-medium transition ${
                    filter === 'buy'
                      ? 'bg-green-600 text-white'
                      : 'bg-green-100 text-green-600 hover:bg-green-200'
                  }`}
                >
                  Buy
                </button>
                <button
                  onClick={() => setFilter('sell')}
                  className={`px-3 py-1 rounded-lg text-sm font-medium transition ${
                    filter === 'sell'
                      ? 'bg-red-600 text-white'
                      : 'bg-red-100 text-red-600 hover:bg-red-200'
                  }`}
                >
                  Sell
                </button>
              </div>
            </div>

            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[1, 2, 3, 4].map((i) => (
                  <div
                    key={i}
                    className="bg-white rounded-xl shadow-lg p-6 animate-pulse"
                  >
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
                <p className="text-gray-500">No signals found</p>
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
          <SignalDetail
            signal={selectedSignal}
            onClose={() => setSelectedSignal(null)}
          />
        )}
      </div>
    </main>
  );
}
