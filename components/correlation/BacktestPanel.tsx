"use client";

import { useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import { PairInfo, BacktestResponse } from "@/lib/correlationTypes";

interface BacktestPanelProps {
  pair: PairInfo;
  dateRange: { start: string; end: string };
  spreadType: string;
}

const TOOLTIP_STYLE = {
  backgroundColor: "rgba(0,0,0,0.85)",
  border: "1px solid rgba(255,255,255,0.1)",
  borderRadius: "12px",
  backdropFilter: "blur(12px)",
  fontSize: 12,
  color: "#e5e5e5",
};

const AXIS_TICK = { fill: "#737373", fontSize: 10 };
const AXIS_LINE = { stroke: "rgba(255,255,255,0.06)" };
const GRID = "rgba(255,255,255,0.04)";

function formatDate(d: string) {
  const date = new Date(d);
  return date.toLocaleDateString("en-US", { month: "short", year: "2-digit" });
}

export default function BacktestPanel({
  pair,
  dateRange,
  spreadType,
}: BacktestPanelProps) {
  const [windowVal, setWindowVal] = useState("20");
  const [entryZ, setEntryZ] = useState("2.0");
  const [exitZ, setExitZ] = useState("0.0");
  const [hedgeRatio, setHedgeRatio] = useState("1.0");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<BacktestResponse | null>(null);

  const runBacktest = async () => {
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const params = new URLSearchParams({
        ticker_a: pair.ticker_a,
        ticker_b: pair.ticker_b,
        start: dateRange.start,
        end: dateRange.end,
        spread_type: spreadType,
        window: windowVal,
        entry_z: entryZ,
        exit_z: exitZ,
        hedge_ratio: hedgeRatio,
      });

      const res = await fetch(`/api/backtest?${params.toString()}`);
      
      if (!res.ok) {
        let msg = "Failed to run backtest";
        try {
          const errBody = await res.json();
          if (errBody.error) msg = errBody.error;
        } catch {}
        throw new Error(msg);
      }

      const data: BacktestResponse = await res.json();
      setResults(data);
    } catch (err: any) {
      setError(err.message || "An unknown error occurred");
    } finally {
      setLoading(false);
    }
  };

  const chartData = results?.equity_curve.map((item) => ({
    ...item,
    formattedReturn: item.value * 100,
  })) || [];
  
  const everyN = Math.max(1, Math.floor(chartData.length / 12));

  return (
    <div className="space-y-6">
      {/* Configuration Form */}
      <div className="rounded-2xl border border-white/[0.08] bg-white/[0.02] p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-neutral-300">
            Backtest Configuration
          </h3>
          <button
            onClick={runBacktest}
            disabled={loading}
            className="px-4 py-1.5 rounded-lg bg-[#c28b00] text-black font-semibold text-sm hover:bg-[#dca311] transition-colors disabled:opacity-50 flex items-center gap-2"
          >
            {loading && (
              <div className="h-3 w-3 border-2 border-black/30 border-t-black rounded-full animate-spin" />
            )}
            {loading ? "Running..." : "Run Backtest"}
          </button>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div>
            <label className="block text-[10px] uppercase tracking-widest text-neutral-500 mb-1">
              Window
            </label>
            <input
              type="number"
              value={windowVal}
              onChange={(e) => setWindowVal(e.target.value)}
              className="w-full bg-black/40 border border-white/10 rounded-md px-3 py-1.5 text-sm text-neutral-200 focus:outline-none focus:border-[#c28b00]"
            />
          </div>
          <div>
            <label className="block text-[10px] uppercase tracking-widest text-neutral-500 mb-1">
              Entry Z-Score
            </label>
            <input
              type="number"
              step="0.1"
              value={entryZ}
              onChange={(e) => setEntryZ(e.target.value)}
              className="w-full bg-black/40 border border-white/10 rounded-md px-3 py-1.5 text-sm text-neutral-200 focus:outline-none focus:border-[#c28b00]"
            />
          </div>
          <div>
            <label className="block text-[10px] uppercase tracking-widest text-neutral-500 mb-1">
              Exit Z-Score
            </label>
            <input
              type="number"
              step="0.1"
              value={exitZ}
              onChange={(e) => setExitZ(e.target.value)}
              className="w-full bg-black/40 border border-white/10 rounded-md px-3 py-1.5 text-sm text-neutral-200 focus:outline-none focus:border-[#c28b00]"
            />
          </div>
          <div>
            <label className="block text-[10px] uppercase tracking-widest text-neutral-500 mb-1">
              Hedge Ratio
            </label>
            <input
              type="number"
              step="0.1"
              value={hedgeRatio}
              onChange={(e) => setHedgeRatio(e.target.value)}
              className="w-full bg-black/40 border border-white/10 rounded-md px-3 py-1.5 text-sm text-neutral-200 focus:outline-none focus:border-[#c28b00]"
            />
          </div>
        </div>

        {error && (
          <div className="mt-4 rounded-lg border border-red-500/20 bg-red-500/5 p-3 text-sm text-red-400">
            {error}
          </div>
        )}
      </div>

      {results && (
        <div className="space-y-6">
          {/* Metrics Panel */}
          <div className="rounded-xl border border-white/[0.08] bg-white/[0.02] px-2 py-2.5">
            <div className="flex flex-wrap items-center gap-y-2">
              <div className="flex items-center gap-1.5 px-3">
                <span className="text-[10px] uppercase tracking-widest text-neutral-500">Sharpe</span>
                <span className={`text-sm font-mono tabular-nums font-semibold ${results.metrics.sharpe >= 0 ? "text-green-500" : "text-red-500"}`}>
                  {results.metrics.sharpe.toFixed(2)}
                </span>
              </div>
              <div className="w-px self-stretch bg-white/[0.06]" />
              <div className="flex items-center gap-1.5 px-3">
                <span className="text-[10px] uppercase tracking-widest text-neutral-500">Max DD</span>
                <span className="text-sm font-mono tabular-nums text-red-400">
                  {(results.metrics.max_drawdown * 100).toFixed(2)}%
                </span>
              </div>
              <div className="w-px self-stretch bg-white/[0.06]" />
              <div className="flex items-center gap-1.5 px-3">
                <span className="text-[10px] uppercase tracking-widest text-neutral-500">Trades</span>
                <span className="text-sm font-mono tabular-nums text-neutral-200">
                  {results.metrics.num_trades}
                </span>
              </div>
              <div className="w-px self-stretch bg-white/[0.06]" />
              <div className="flex items-center gap-1.5 px-3">
                <span className="text-[10px] uppercase tracking-widest text-neutral-500">Win Rate</span>
                <span className="text-sm font-mono tabular-nums text-neutral-200">
                  {(results.metrics.win_rate * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          </div>

          {/* Equity Curve Chart */}
          <div className="rounded-2xl border border-white/[0.08] bg-white/[0.02] p-5">
            <h3 className="text-sm font-semibold text-neutral-300 mb-1">
              Equity Curve
            </h3>
            <p className="text-xs text-neutral-500 mb-4">
              Cumulative returns over the backtest period
            </p>
            <div className="h-[250px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={GRID} />
                  <XAxis
                    dataKey="date"
                    tick={AXIS_TICK}
                    axisLine={AXIS_LINE}
                    tickLine={false}
                    tickFormatter={formatDate}
                    interval={everyN}
                  />
                  <YAxis
                    tick={AXIS_TICK}
                    axisLine={AXIS_LINE}
                    tickLine={false}
                    tickFormatter={(val) => `${val.toFixed(1)}%`}
                  />
                  <Tooltip
                    contentStyle={TOOLTIP_STYLE}
                    labelFormatter={(l) => `Date: ${l}`}
                    formatter={(value: number) => [`${value.toFixed(2)}%`, "Return"]}
                  />
                  <Line
                    type="monotone"
                    dataKey="formattedReturn"
                    stroke="#10b981"
                    strokeWidth={1.5}
                    dot={false}
                    activeDot={{ r: 4, fill: "#10b981" }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Trade Log */}
          <div className="rounded-2xl border border-white/[0.08] bg-white/[0.02] overflow-hidden">
            <div className="p-5 border-b border-white/[0.06]">
              <h3 className="text-sm font-semibold text-neutral-300">
                Trade Log
              </h3>
            </div>
            
            {results.trade_log.length === 0 ? (
              <div className="p-8 text-center text-sm text-neutral-500">
                No trades executed during this period.
              </div>
            ) : (
              <div className="overflow-x-auto max-h-[400px]">
                <table className="w-full text-left text-xs whitespace-nowrap">
                  <thead className="bg-black/80 text-neutral-500 uppercase tracking-wider sticky top-0 backdrop-blur-md z-10">
                    <tr>
                      <th className="px-4 py-3 font-medium">Type</th>
                      <th className="px-4 py-3 font-medium">Entry Date</th>
                      <th className="px-4 py-3 font-medium">Exit Date</th>
                      <th className="px-4 py-3 font-medium">Spread (In / Out)</th>
                      <th className="px-4 py-3 font-medium">Prices A/B (In)</th>
                      <th className="px-4 py-3 font-medium">Prices A/B (Out)</th>
                      <th className="px-4 py-3 font-medium">Hold (Days)</th>
                      <th className="px-4 py-3 font-medium text-right">PnL</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/[0.04]">
                    {results.trade_log.map((trade, idx) => (
                      <tr key={idx} className="hover:bg-white/[0.02] transition-colors">
                        <td className="px-4 py-3">
                          <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium tracking-widest uppercase ${
                            trade.type === "LONG" ? "bg-green-500/10 text-green-400" : "bg-purple-500/10 text-purple-400"
                          }`}>
                            {trade.type}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-neutral-300">{trade.entry_date}</td>
                        <td className="px-4 py-3 text-neutral-300">{trade.exit_date}</td>
                        <td className="px-4 py-3 text-neutral-400 font-mono">
                          {trade.entry_spread.toFixed(3)} → {trade.exit_spread.toFixed(3)}
                        </td>
                        <td className="px-4 py-3 text-neutral-400 font-mono">
                          {trade.entry_price_a.toFixed(2)} / {trade.entry_price_b.toFixed(2)}
                        </td>
                        <td className="px-4 py-3 text-neutral-400 font-mono">
                          {trade.exit_price_a.toFixed(2)} / {trade.exit_price_b.toFixed(2)}
                        </td>
                        <td className="px-4 py-3 text-neutral-400 text-center">{trade.holding_period}</td>
                        <td className="px-4 py-3 text-right">
                          <div className={`font-mono font-medium ${trade.pnl_val >= 0 ? "text-green-500" : "text-red-500"}`}>
                            {trade.pnl_val >= 0 ? "+" : ""}{trade.pnl_val.toFixed(2)}
                            <span className="ml-1 opacity-80 text-[10px]">
                              ({trade.pnl_pct >= 0 ? "+" : ""}{(trade.pnl_pct * 100).toFixed(2)}%)
                            </span>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
