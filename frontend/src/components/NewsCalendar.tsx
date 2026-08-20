'use client';

import { NewsEvent } from '@/types';
import { Calendar, AlertCircle, Clock } from 'lucide-react';

interface NewsCalendarProps {
  events: NewsEvent[];
  currentWarnings: string[];
}

export default function NewsCalendar({ events, currentWarnings }: NewsCalendarProps) {
  const getImpactColor = (impact: string) => {
    switch (impact.toLowerCase()) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getCountryFlag = (country: string) => {
    const flags: Record<string, string> = {
      USD: '🇺🇸',
      EUR: '🇪🇺',
      GBP: '🇬🇧',
      JPY: '🇯🇵',
      AUD: '🇦🇺',
      CAD: '🇨🇦',
      CHF: '🇨🇭',
      NZD: '🇳🇿',
    };
    return flags[country] || '🌍';
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Calendar className="w-5 h-5 text-blue-500" />
          <h2 className="text-lg font-bold text-gray-900">Economic Calendar</h2>
        </div>
        {currentWarnings.length > 0 && (
          <div className="flex items-center gap-2 bg-red-50 px-3 py-1 rounded-full">
            <AlertCircle className="w-4 h-4 text-red-500" />
            <span className="text-xs font-medium text-red-700">High Impact Period</span>
          </div>
        )}
      </div>

      {currentWarnings.length > 0 && (
        <div className="mb-6 p-4 bg-red-50 rounded-lg border border-red-200">
          <p className="text-sm font-medium text-red-800 mb-2">⚠️ Current Warnings:</p>
          <ul className="space-y-1">
            {currentWarnings.map((warning, idx) => (
              <li key={idx} className="text-sm text-red-700">
                • {warning}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {events.length === 0 ? (
          <p className="text-center text-gray-500 py-8">No upcoming events</p>
        ) : (
          events.map((event, idx) => (
            <div
              key={idx}
              className={`p-4 rounded-lg border ${getImpactColor(event.impact)}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{getCountryFlag(event.country)}</span>
                  <div>
                    <p className="font-semibold">{event.title}</p>
                    <p className="text-sm opacity-75">{event.country}</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="flex items-center gap-1 text-sm">
                    <Clock className="w-3 h-3" />
                    {event.time}
                  </div>
                  <p className="text-xs opacity-75">{event.date}</p>
                </div>
              </div>

              <div className="mt-3 grid grid-cols-3 gap-2 text-sm">
                <div>
                  <p className="opacity-75 text-xs">Forecast</p>
                  <p className="font-medium">{event.forecast || '-'}</p>
                </div>
                <div>
                  <p className="opacity-75 text-xs">Previous</p>
                  <p className="font-medium">{event.previous || '-'}</p>
                </div>
                <div>
                  <p className="opacity-75 text-xs">Actual</p>
                  <p className="font-medium">{event.actual || 'Pending'}</p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
