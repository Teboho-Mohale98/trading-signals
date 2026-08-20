'use client';

import { Signal } from '@/types';
import { X, TrendingUp, TrendingDown, Target, Shield, BarChart3 } from 'lucide-react';

interface SignalDetailProps {
  signal: Signal;
  onClose: () => void;
}

export default function SignalDetail({ signal, onClose }: SignalDetailProps) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {signal.signal_type.includes('BUY') ? (
                <TrendingUp className="w-8 h-8 text-buy" />
              ) : signal.signal_type.includes('SELL') ? (
                <TrendingDown className="w-8 h-8 text-sell" />
              ) : (
                <BarChart3 className="w-8 h-8 text-neutral" />
              )}
              <div>
                <h2 className="text-2xl font-bold">{signal.symbol}</h2>
                <p className="text-gray-500">{signal.timeframe} Timeframe</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-full transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="p-6">
          <div className="text-center mb-6">
            <span
              className={`text-4xl font-bold ${
                signal.signal_type.includes('BUY')
                  ? 'text-buy'
                  : signal.signal_type.includes('SELL')
                  ? 'text-sell'
                  : 'text-neutral'
              }`}
            >
              {signal.signal_type}
            </span>
            <p className="text-gray-500 mt-1">Signal Strength: {signal.strength}</p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-gray-50 rounded-lg p-4 text-center">
              <Target className="w-5 h-5 mx-auto text-blue-500 mb-2" />
              <p className="text-xs text-gray-500">Entry Price</p>
              <p className="text-lg font-bold">{signal.price}</p>
            </div>
            <div className="bg-red-50 rounded-lg p-4 text-center">
              <Shield className="w-5 h-5 mx-auto text-red-500 mb-2" />
              <p className="text-xs text-gray-500">Stop Loss</p>
              <p className="text-lg font-bold text-red-600">{signal.stop_loss}</p>
            </div>
            <div className="bg-green-50 rounded-lg p-4 text-center">
              <TrendingUp className="w-5 h-5 mx-auto text-green-500 mb-2" />
              <p className="text-xs text-gray-500">Take Profit</p>
              <p className="text-lg font-bold text-green-600">{signal.take_profit}</p>
            </div>
            <div className="bg-yellow-50 rounded-lg p-4 text-center">
              <BarChart3 className="w-5 h-5 mx-auto text-yellow-500 mb-2" />
              <p className="text-xs text-gray-500">Risk:Reward</p>
              <p className="text-lg font-bold">1:{signal.risk_reward}</p>
            </div>
          </div>

          {signal.indicators && (
            <div className="mb-6">
              <h3 className="font-semibold text-gray-900 mb-3">Technical Indicators</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500">RSI (14)</p>
                  <p className={`font-bold ${
                    signal.indicators.rsi > 70 ? 'text-red-600' :
                    signal.indicators.rsi < 30 ? 'text-green-600' : 'text-gray-900'
                  }`}>
                    {signal.indicators.rsi}
                  </p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500">MACD</p>
                  <p className="font-bold">{signal.indicators.macd}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500">BB %</p>
                  <p className="font-bold">{signal.indicators.bb_pct}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500">ATR</p>
                  <p className="font-bold">{signal.indicators.atr}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500">Volume Ratio</p>
                  <p className="font-bold">{signal.indicators.volume_ratio}x</p>
                </div>
              </div>
            </div>
          )}

          {signal.price_data && (
            <div className="mb-6">
              <h3 className="font-semibold text-gray-900 mb-3">Price Levels</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-gray-500">Current Price</p>
                    <p className="font-bold">{signal.price_data.close}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Support 1</p>
                    <p className="font-bold text-green-600">{signal.price_data.support_1}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Resistance 1</p>
                    <p className="font-bold text-red-600">{signal.price_data.resistance_1}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Day Range</p>
                    <p className="font-bold">
                      {signal.price_data.low} - {signal.price_data.high}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="mb-6">
            <h3 className="font-semibold text-gray-900 mb-3">Analysis Reasons</h3>
            <ul className="space-y-2">
              {signal.reasons.map((reason, idx) => (
                <li key={idx} className="flex items-start gap-2 text-gray-700">
                  <span className={`mt-1 w-2 h-2 rounded-full ${
                    signal.signal_type.includes('BUY') ? 'bg-green-500' :
                    signal.signal_type.includes('SELL') ? 'bg-red-500' : 'bg-gray-500'
                  }`} />
                  {reason}
                </li>
              ))}
            </ul>
          </div>

          <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
            <p className="text-sm text-yellow-800">
              <strong>⚠️ Disclaimer:</strong> This is not financial advice. Trading involves substantial risk of loss. 
              Always do your own research and never trade with money you cannot afford to lose.
            </p>
          </div>

          <div className="mt-4 text-center text-sm text-gray-400">
            Generated: {new Date(signal.timestamp).toLocaleString()}
          </div>
        </div>
      </div>
    </div>
  );
}
