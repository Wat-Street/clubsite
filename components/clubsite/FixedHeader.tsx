"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";
import Header from "@/components/clubsite/Header";

const ROUTE_BANNERS: Record<string, string> = {
  "/correlation-trading": "Work in progress — data unavailable at this time",
};

const DEFAULT_PAGES: Record<string, number> = {
  "/": 0,
  "/research": 3,
  "/correlation-trading": -1,
};

const BANNER_HEIGHT = 32;
const HEADER_HEIGHT = 96;
const REVEAL_DELAY_MS = 350;
const TRANSITION = { duration: 0.55, ease: [0.22, 1, 0.36, 1] as const };

export default function FixedHeader() {
  const pathname = usePathname() ?? "/";
  const bannerText = ROUTE_BANNERS[pathname] ?? null;
  const defaultPage = DEFAULT_PAGES[pathname] ?? -1;
  const showSiteHeader = pathname !== "/correlation-trading";

  const [activeBanner, setActiveBanner] = useState<string | null>(null);
  const [dismissed, setDismissed] = useState(false);

  const storageKey = `banner-dismissed:${pathname}`;

  // Read persisted dismissal whenever the route changes
  useEffect(() => {
    if (typeof window === "undefined") return;
    setDismissed(window.localStorage.getItem(storageKey) === "true");
  }, [storageKey]);

  // Wait for the route to settle before triggering the reveal animation
  useEffect(() => {
    if (!bannerText) {
      setActiveBanner(null);
      return;
    }
    const id = window.setTimeout(() => setActiveBanner(bannerText), REVEAL_DELAY_MS);
    return () => window.clearTimeout(id);
  }, [bannerText]);

  const handleDismiss = () => {
    setDismissed(true);
    if (typeof window !== "undefined") {
      window.localStorage.setItem(storageKey, "true");
    }
  };

  const showBanner = !!activeBanner && !dismissed;
  const spacerHeight =
    (showBanner ? BANNER_HEIGHT : 0) + (showSiteHeader ? HEADER_HEIGHT : 0);

  useEffect(() => {
    if (typeof document === "undefined") return;
    document.documentElement.style.setProperty(
      "--fixed-header-offset",
      `${spacerHeight}px`
    );

    return () => {
      document.documentElement.style.removeProperty("--fixed-header-offset");
    };
  }, [spacerHeight]);

  return (
    <>
      <div className="fixed top-0 left-0 right-0 z-40">
        <AnimatePresence initial={false}>
          {showBanner && (
            <motion.div
              key="banner"
              initial={{ height: 0 }}
              animate={{ height: BANNER_HEIGHT }}
              exit={{ height: 0 }}
              transition={TRANSITION}
              className="overflow-hidden bg-[#E39403]"
            >
              <div className="relative h-8 flex items-center justify-center text-xs text-white px-4">
                <span>{activeBanner}</span>
                <button
                  onClick={handleDismiss}
                  aria-label="Dismiss banner"
                  className="absolute right-3 top-1/2 -translate-y-1/2 p-1"
                >
                  <X
                    size={14}
                    strokeWidth={2.5}
                    className="opacity-70 hover:opacity-100 transition-opacity"
                  />
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        {showSiteHeader && (
          <div className="bg-black">
            <Header defaultPage={defaultPage} />
          </div>
        )}
      </div>
      <motion.div
        initial={false}
        animate={{ height: spacerHeight }}
        transition={TRANSITION}
        aria-hidden
      />
    </>
  );
}
