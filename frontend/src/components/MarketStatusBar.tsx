'use client';

import { MarketStatus } from '@/types';
import { Activity, Globe, Clock } from 'lucide-react';

interface MarketStatusProps {
  status: MarketStatus;
}

export default function MarketStatusBar({ status }: MarketStatusProps) {
  const getMarketIndicator = (marketStatus: string) => {
    return marketStatus === 'Open' ? (
      <span className="flex items-center gap-1">
        <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
        <span className="text-green-700 font-medium">Open</span>
      </span>
    ) : (
      <span className="flex items-center gap-1">
        <span className="w-2 h-2 bg-red-500 rounded-full" />
        <span className="text-red-700 font-medium">Closed</span>
      </span>
    );
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-4 border border-gray-100">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-blue-500" />
          <h3 className="font-semibold text-gray-900">Market Status</h3>
        </div>
        <div className="flex items-center gap-1 text-sm text-gray-500">
          <Clock className="w-4 h-4" />
          {new Date(status.timestamp).toLocaleTimeString()}
        </div>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-4">
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center gap-2">
            <Globe className="w-4 h-4 text-gray-500" />
            <span className="text-sm font-medium">Forex</span>
          </div>
          {getMarketIndicator(status.forex)}
        </div>
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center gap-2">
            <Globe className="w-4 h-4 text-gray-500" />
            <span className="text-sm font-medium">Stocks</span>
          </div>
          {getMarketIndicator(status.stocks)}
        </div>
      </div>
    </div>
  );
}
