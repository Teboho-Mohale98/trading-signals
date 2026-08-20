export interface Signal {
  symbol: string;
  signal_type: 'BUY' | 'SELL' | 'STRONG_BUY' | 'STRONG_SELL' | 'NEUTRAL';
  strength: 'STRONG' | 'MODERATE' | 'WEAK';
  price: number;
  reasons: string[];
  stop_loss: number;
  take_profit: number;
  risk_reward: number;
  timestamp: string;
  timeframe: string;
  indicators?: {
    rsi: number;
    macd: number;
    macd_signal: number;
    bb_pct: number;
    atr: number;
    volume_ratio: number;
  };
  price_data?: {
    open: number;
    high: number;
    low: number;
    close: number;
    support_1: number;
    resistance_1: number;
  };
}

export interface NewsEvent {
  title: string;
  country: string;
  date: string;
  time: string;
  impact: string;
  forecast: string | null;
  previous: string | null;
  actual: string | null;
}

export interface MarketStatus {
  forex: string;
  stocks: string;
  timestamp: string;
}

export interface SignalsResponse {
  total_signals: number;
  actionable_signals: number;
  signals: Signal[];
  all_signals: Signal[];
  generated_at: string;
}

export interface NewsResponse {
  upcoming_events: NewsEvent[];
  current_status: {
    is_high_impact: boolean;
    warnings: string[];
    timestamp: string;
  };
}
