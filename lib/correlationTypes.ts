export interface PairInfo {
  ticker_a: string;
  ticker_b: string;
  name_a: string;
  name_b: string;
  sector: string;
  category?: "popular" | "tradeable";
}

export interface CorrelationPoint {
  lag: number;
  correlation: number | null;
}

export interface CorrelationResponse {
  ticker_a: string;
  ticker_b: string;
  data: CorrelationPoint[];
}

export interface SpreadPoint {
  date: string;
  price_a: number | null;
  price_b: number | null;
  norm_a: number | null;
  norm_b: number | null;
  spread: number | null;
  zscore: number | null;
}

export interface SpreadMetrics {
  spread_type: string;
  ticker_a: string;
  ticker_b: string;
  num_observations: number;
  mean: number;
  std: number;
  min: number;
  max: number;
  current: number;
  current_zscore: number;
}

export interface SpreadResponse {
  ticker_a: string;
  ticker_b: string;
  spread_type: string;
  data: SpreadPoint[];
  metrics: SpreadMetrics;
}

export interface RiskBreakdownResponse {
  ticker_a: string;
  ticker_b: string;
  current_corr: number | null;
  baseline_corr: number | null;
  broken: boolean;
  broken_since: string | null;
}

export type SignalLevel = "normal" | "watch" | "signal";
export type SignalDirection = "long" | "short" | "hold";

export const SECTOR_COLORS: Record<string, string> = {
  Technology: "#8b5cf6",
  Healthcare: "#06b6d4",
  Consumer: "#f59e0b",
  Industrials: "#6b7280",
  Financials: "#3b82f6",
  Energy: "#ef4444",
  Telecom: "#10b981",
  Retail: "#ec4899",
  "Real Estate": "#f97316",
};

export const PAIRS: PairInfo[] = [
  // Popular / well-known pairs
  { ticker_a: "MSFT",  ticker_b: "GOOGL", name_a: "Microsoft",         name_b: "Google",            sector: "Technology", category: "popular" },
  { ticker_a: "AMD",   ticker_b: "NVDA",  name_a: "AMD",               name_b: "NVIDIA",            sector: "Technology", category: "popular" },
  { ticker_a: "CVS",   ticker_b: "JNJ",   name_a: "CVS Health",        name_b: "Johnson & Johnson", sector: "Healthcare", category: "popular" },
  { ticker_a: "PFE",   ticker_b: "MRK",   name_a: "Pfizer",            name_b: "Merck",             sector: "Healthcare", category: "popular" },
  { ticker_a: "CL",    ticker_b: "KMB",   name_a: "Colgate-Palmolive", name_b: "Kimberly-Clark",    sector: "Consumer",   category: "popular" },
  { ticker_a: "KO",    ticker_b: "PEP",   name_a: "Coca-Cola",         name_b: "PepsiCo",           sector: "Consumer",   category: "popular" },
  { ticker_a: "COST",  ticker_b: "BJ",    name_a: "Costco",            name_b: "BJ's Wholesale",    sector: "Retail",     category: "popular" },
  { ticker_a: "GE",    ticker_b: "BA",    name_a: "GE Aerospace",      name_b: "Boeing",            sector: "Industrials",category: "popular" },
  { ticker_a: "V",     ticker_b: "MA",    name_a: "Visa",              name_b: "Mastercard",        sector: "Financials", category: "popular" },
  { ticker_a: "MS",    ticker_b: "GS",    name_a: "Morgan Stanley",    name_b: "Goldman Sachs",     sector: "Financials", category: "popular" },
  { ticker_a: "JPM",   ticker_b: "BAC",   name_a: "JPMorgan Chase",    name_b: "Bank of America",   sector: "Financials", category: "popular" },
  { ticker_a: "XOM",   ticker_b: "CVX",   name_a: "ExxonMobil",        name_b: "Chevron",           sector: "Energy",     category: "popular" },
  { ticker_a: "T",     ticker_b: "VZ",    name_a: "AT&T",              name_b: "Verizon",           sector: "Telecom",    category: "popular" },
  { ticker_a: "WMT",   ticker_b: "TGT",   name_a: "Walmart",           name_b: "Target",            sector: "Retail",     category: "popular" },
  // Most tradeable — validated cointegrated pairs (p < 0.05, Engle-Granger, 2020-present)
  { ticker_a: "STX",  ticker_b: "WDC",  name_a: "Seagate Technology",       name_b: "Western Digital",         sector: "Technology",  category: "tradeable" },
  { ticker_a: "ADI",  ticker_b: "AMAT", name_a: "Analog Devices",           name_b: "Applied Materials",       sector: "Technology",  category: "tradeable" },
  { ticker_a: "LLY",  ticker_b: "AMGN", name_a: "Eli Lilly",                name_b: "Amgen",                   sector: "Healthcare",  category: "tradeable" },
  { ticker_a: "TMO",  ticker_b: "MTD",  name_a: "Thermo Fisher Scientific", name_b: "Mettler-Toledo",          sector: "Healthcare",  category: "tradeable" },
  { ticker_a: "TMO",  ticker_b: "IQV",  name_a: "Thermo Fisher Scientific", name_b: "IQVIA Holdings",          sector: "Healthcare",  category: "tradeable" },
  { ticker_a: "A",    ticker_b: "IQV",  name_a: "Agilent Technologies",     name_b: "IQVIA Holdings",          sector: "Healthcare",  category: "tradeable" },
  { ticker_a: "PNC",  ticker_b: "FITB", name_a: "PNC Financial",            name_b: "Fifth Third Bancorp",     sector: "Financials",  category: "tradeable" },
  { ticker_a: "GS",   ticker_b: "BK",   name_a: "Goldman Sachs",            name_b: "Bank of New York Mellon", sector: "Financials",  category: "tradeable" },
  { ticker_a: "MS",   ticker_b: "BK",   name_a: "Morgan Stanley",           name_b: "Bank of New York Mellon", sector: "Financials",  category: "tradeable" },
  { ticker_a: "WMB",  ticker_b: "EPD",  name_a: "Williams Companies",       name_b: "Enterprise Products",     sector: "Energy",      category: "tradeable" },
  { ticker_a: "REG",  ticker_b: "BRX",  name_a: "Regency Centers",          name_b: "Brixmor Property Group",  sector: "Real Estate", category: "tradeable" },
  { ticker_a: "UDR",  ticker_b: "CPT",  name_a: "UDR Inc",                  name_b: "Camden Property Trust",   sector: "Real Estate", category: "tradeable" },
  { ticker_a: "UNP",  ticker_b: "CSX",  name_a: "Union Pacific",            name_b: "CSX Corporation",         sector: "Industrials", category: "tradeable" },
  { ticker_a: "ABNB", ticker_b: "TRIP", name_a: "Airbnb",                   name_b: "Tripadvisor",             sector: "Consumer",    category: "tradeable" },
];

export function getSignalLevel(zscore: number): SignalLevel {
  const abs = Math.abs(zscore);
  if (abs >= 2) return "signal";
  if (abs >= 1) return "watch";
  return "normal";
}

export function getSignalDirection(zscore: number): SignalDirection {
  if (zscore > 2) return "short";
  if (zscore < -2) return "long";
  return "hold";
}

export function getSignalColor(level: SignalLevel): string {
  if (level === "signal") return "#ef4444";
  if (level === "watch") return "#f59e0b";
  return "#22c55e";
}
