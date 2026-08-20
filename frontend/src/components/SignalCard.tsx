'use client';

import { Signal } from '@/types';
import { TrendingUp, TrendingDown, Minus, AlertTriangle, Target, Shield } from 'lucide-react';

interface SignalCardProps {
  signal: Signal;
  onClick?: () => void;
}

export default function SignalCard({ signal, onClick }: SignalCardProps) {
  const getSignalIcon = () => {
    switch (signal.signal_type) {
      case 'STRONG_BUY':
      case 'BUY':
        return <TrendingUp className="w-6 h-6 text-buy" />;
      case 'STRONG_SELL':
      case 'SELL':
        return <TrendingDown className="w-6 h-6 text-sell" />;
      default:
        return <Minus className="w-6 h-6 text-neutral" />;
    }
  };

  const getSignalColor = () => {
    switch (signal.signal_type) {
      case 'STRONG_BUY':
      case 'BUY':
        return 'signal-buy';
      case 'STRONG_SELL':
      case 'SELL':
        return 'signal-sell';
      default:
        return 'signal-neutral';
    }
  };

  const getStrengthBadge = () => {
    switch (signal.strength) {
      case 'STRONG':
        return <span className="indicator-badge badge-strong">STRONG</span>;
      case 'MODERATE':
        return <span className="indicator-badge badge-moderate">MODERATE</span>;
      default:
        return <span className="indicator-badge badge-weak">WEAK</span>;
    }
  };

  return (
    <div
      className={`signal-card ${getSignalColor()} cursor-pointer`}
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          {getSignalIcon()}
          <div>
            <h3 className="text-lg font-bold text-gray-900">{signal.symbol}</h3>
            <p className="text-sm text-gray-500">{signal.timeframe} Timeframe</p>
          </div>
        </div>
        {getStrengthBadge()}
      </div>

      <div className="mb-4">
        <span
          className={`text-2xl font-bold ${
            signal.signal_type.includes('BUY')
              ? 'text-buy'
              : signal.signal_type.includes('SELL')
              ? 'text-sell'
              : 'text-neutral'
          }`}
        >
          {signal.signal_type}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="flex items-center gap-2">
          <Target className="w-4 h-4 text-gray-400" />
          <div>
            <p className="text-xs text-gray-500">Entry</p>
            <p className="text-sm font-semibold">{signal.price}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Shield className="w-4 h-4 text-red-400" />
          <div>
            <p className="text-xs text-gray-500">Stop Loss</p>
            <p className="text-sm font-semibold text-red-600">{signal.stop_loss}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-green-400" />
          <div>
            <p className="text-xs text-gray-500">Take Profit</p>
            <p className="text-sm font-semibold text-green-600">{signal.take_profit}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-yellow-400" />
          <div>
            <p className="text-xs text-gray-500">Risk:Reward</p>
            <p className="text-sm font-semibold">1:{signal.risk_reward}</p>
          </div>
        </div>
      </div>

      {signal.reasons.length > 0 && (
        <div className="border-t pt-4">
          <p className="text-xs font-medium text-gray-500 mb-2">KEY REASONS</p>
          <ul className="space-y-1">
            {signal.reasons.slice(0, 3).map((reason, idx) => (
              <li key={idx} className="text-xs text-gray-600 flex items-start gap-2">
                <span className="text-green-500 mt-0.5">•</span>
                {reason}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-4 text-xs text-gray-400">
        {new Date(signal.timestamp).toLocaleString()}
      </div>
    </div>
  );
}
