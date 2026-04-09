"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";

import Header from "@/components/clubsite/Header";
import Footer from "@/components/clubsite/Footer";

import PairSelector from "@/components/correlation/PairSelector";
import ControlsBar from "@/components/correlation/ControlsBar";
import LagCorrelationChart from "@/components/correlation/LagCorrelationChart";
import SpreadAnalysisCharts from "@/components/correlation/SpreadAnalysisCharts";
import MetricsPanel from "@/components/correlation/MetricsPanel";
import SpreadHistogram from "@/components/correlation/SpreadHistogram";

import type {
  PairInfo,
  CorrelationResponse,
  SpreadResponse,
  SignalLevel,
} from "@/lib/correlationTypes";
import { getSignalLevel, PAIRS } from "@/lib/correlationTypes";

const API_BASE = "/api";

function yearsAgo(n: number): string {
  const d = new Date();
  d.setFullYear(d.getFullYear() - n);
  return d.toISOString().split("T")[0];
}

export default function CorrelationTestingPage() {
  const [selectedPair, setSelectedPair] = useState<PairInfo | null>(null);
  const [dateRange, setDateRange] = useState({
    start: yearsAgo(3),
    end: new Date().toISOString().split("T")[0],
  });
  const [spreadType, setSpreadType] = useState("log_ratio");
  const [loading, setLoading] = useState(false);
  const [corrData, setCorrData] = useState<CorrelationResponse | null>(null);
  const [spreadData, setSpreadData] = useState<SpreadResponse | null>(null);
  const [pairSignals, setPairSignals] = useState<Record<string, SignalLevel>>({});
  const [error, setError] = useState<string | null>(null);

  const fetchAnalysis = useCallback(
    async (pair: PairInfo) => {
      setLoading(true);
      setError(null);
      setCorrData(null);
      setSpreadData(null);

      try {
        const [corrRes, spreadRes] = await Promise.all([
          fetch(
            `${API_BASE}/correlation?ticker_a=${pair.ticker_a}&ticker_b=${pair.ticker_b}&start=${dateRange.start}&end=${dateRange.end}`
          ),
          fetch(
            `${API_BASE}/spread?ticker_a=${pair.ticker_a}&ticker_b=${pair.ticker_b}&start=${dateRange.start}&end=${dateRange.end}&spread_type=${spreadType}`
          ),
        ]);

        if (!corrRes.ok || !spreadRes.ok) {
          const errBody = await (corrRes.ok ? spreadRes : corrRes).json();
          throw new Error(errBody.error || "API error");
        }

        const corr: CorrelationResponse = await corrRes.json();
        const spread: SpreadResponse = await spreadRes.json();

        setCorrData(corr);
        setSpreadData(spread);

        setPairSignals((prev) => ({
          ...prev,
          [`${pair.ticker_a}_${pair.ticker_b}`]: getSignalLevel(
            spread.metrics.current_zscore
          ),
        }));
      } catch (e: any) {
        setError(e.message ?? "Failed to load data");
      } finally {
        setLoading(false);
      }
    },
    [dateRange, spreadType]
  );

  useEffect(() => {
    if (selectedPair) {
      fetchAnalysis(selectedPair);
    }
  }, [selectedPair, dateRange, spreadType, fetchAnalysis]);

  // Pre-fetch signals for all pairs on mount
  useEffect(() => {
    async function prefetch() {
      const signals: Record<string, SignalLevel> = {};
      for (const pair of PAIRS) {
        try {
          const res = await fetch(
            `${API_BASE}/spread?ticker_a=${pair.ticker_a}&ticker_b=${pair.ticker_b}&start=${yearsAgo(1)}&end=${new Date().toISOString().split("T")[0]}&spread_type=log_ratio`
          );
          if (res.ok) {
            const data: SpreadResponse = await res.json();
            signals[`${pair.ticker_a}_${pair.ticker_b}`] = getSignalLevel(
              data.metrics.current_zscore
            );
          }
        } catch {
          // silently skip
        }
      }
      setPairSignals((prev) => ({ ...prev, ...signals }));
    }
    prefetch();
  }, []);

  const handleSelect = (pair: PairInfo) => {
    setSelectedPair(pair);
  };

  const handleBack = () => {
    setSelectedPair(null);
    setCorrData(null);
    setSpreadData(null);
    setError(null);
  };

  return (
    <main className="mx-6 sm:mx-0 min-h-screen">
      <Header defaultPage={-1} />

      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 min-h-[calc(100vh-80px)]">
        <AnimatePresence mode="wait">
          {!selectedPair ? (
            <motion.div
              key="selector"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.25 }}
            >
              <PairSelector
                onSelect={handleSelect}
                selectedPair={selectedPair}
                pairSignals={pairSignals}
              />
            </motion.div>
          ) : (
            <motion.div
              key="analysis"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.25 }}
            >
              <ControlsBar
                pair={selectedPair}
                dateRange={dateRange}
                spreadType={spreadType}
                onDateRangeChange={setDateRange}
                onSpreadTypeChange={setSpreadType}
                onBack={handleBack}
                loading={loading}
              />

              {error && (
                <div className="mt-6 rounded-xl border border-red-500/20 bg-red-500/5 p-4 text-sm text-red-400 text-center">
                  {error}
                </div>
              )}

              {loading && !corrData && (
                <div className="mt-20 text-center">
                  <div className="inline-block h-8 w-8 border-2 border-neutral-700 border-t-[#c28b00] rounded-full animate-spin" />
                  <p className="text-neutral-500 text-sm mt-3">
                    Fetching data for {selectedPair.ticker_a}/{selectedPair.ticker_b}...
                  </p>
                </div>
              )}

              {spreadData && (
                <div className="mt-6 space-y-6">
                  <MetricsPanel metrics={spreadData.metrics} />

                  {corrData && (
                    <LagCorrelationChart
                      data={corrData.data}
                      tickerA={selectedPair.ticker_a}
                      tickerB={selectedPair.ticker_b}
                    />
                  )}

                  <SpreadAnalysisCharts
                    data={spreadData.data}
                    metrics={spreadData.metrics}
                    tickerA={selectedPair.ticker_a}
                    tickerB={selectedPair.ticker_b}
                  />

                  <SpreadHistogram
                    data={spreadData.data}
                    metrics={spreadData.metrics}
                  />
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <Footer />
    </main>
  );
}
