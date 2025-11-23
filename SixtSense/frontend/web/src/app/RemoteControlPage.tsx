// src/pages/RemoteControlPage.tsx

import { useState, useMemo } from "react";
import { Lock, Unlock, Bell, Wifi } from "lucide-react";
import api from "@/api/api";

type Action = "idle" | "locking" | "unlocking" | "blinking";

export default function RemoteControlPage() {
  const [action, setAction] = useState<Action>("idle");
  const [doorsLocked, setDoorsLocked] = useState<boolean | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const bookingId = useMemo(
    () =>
      sessionStorage.getItem("booking_id") ||
      localStorage.getItem("booking_id") ||
      "",
    []
  );

  const isBusy = action !== "idle";
  const isLocking = action === "locking";
  const isUnlocking = action === "unlocking";
  const isBlinking = action === "blinking";

  const callRemoteApi = async (endpoint: string, nextAction: Action) => {
    if (!bookingId) {
      setError("No active booking linked to this device.");
      setMessage(null);
      return;
    }

    setError(null);
    setMessage(null);
    setAction(nextAction);

    try {
      await api.post(endpoint, { booking_id: bookingId });

      if (nextAction === "locking") setDoorsLocked(true);
      if (nextAction === "unlocking") setDoorsLocked(false);

      const label =
        nextAction === "locking"
          ? "Doors locked."
          : nextAction === "unlocking"
          ? "Driver door unlocked."
          : "Lights & horn blinked.";

      setMessage(label);
    } catch (err) {
      console.error(err);
      setError("Something went wrong. Please try again.");
    } finally {
      setAction("idle");
    }
  };

  const handleLock = () =>
    callRemoteApi("/api/ai-engine/car/lock/", "locking");

  const handleUnlock = () =>
    callRemoteApi("/api/ai-engine/car/unlock/", "unlocking");

  const handleBlink = () =>
    callRemoteApi("/api/ai-engine/car/blink/", "blinking");

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-black via-black to-orange-600 flex items-center justify-center px-4 py-6">
      <div className="w-full max-w-md rounded-3xl bg-zinc-950/95 shadow-[0_0_50px_rgba(0,0,0,0.8)] border border-orange-500/40 px-6 py-6 sm:px-8 sm:py-8 backdrop-blur-md">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="inline-flex items-center gap-2 rounded-full bg-zinc-900/80 px-3 py-1 text-[10px] font-medium tracking-[0.22em] uppercase text-orange-400 border border-orange-500/40">
            <Wifi className="w-3 h-3" />
            <span>Remote Key</span>
          </div>

          <div className="flex items-center gap-2 text-[11px] text-zinc-300">
            <span
              className={`relative h-2.5 w-2.5 rounded-full ${
                bookingId ? "bg-emerald-400" : "bg-zinc-600"
              }`}
            >
              {bookingId && (
                <span className="absolute inset-0 rounded-full animate-ping bg-emerald-400/40" />
              )}
            </span>
            <span className="font-medium">
              {bookingId ? (isBusy ? "Working…" : "Connected") : "No booking"}
            </span>
          </div>
        </div>

        <h1 className="text-2xl sm:text-3xl font-semibold text-white mb-1">
          Remote control
        </h1>
        <p className="text-xs sm:text-sm text-zinc-400 mb-6">
          Lock, unlock or blink your SIXT car from this device.
        </p>

        {/* Car display */}
        <div className="overflow-hidden rounded-2xl border border-zinc-800/80 mb-7 bg-gradient-to-br from-zinc-900 via-zinc-950 to-black">
          <div className="h-40 sm:h-44 flex items-end">
            <div className="p-4 sm:p-5 w-full">
              <div className="flex items-center justify-between mb-2">
                <div>
                  <p className="text-[10px] uppercase tracking-[0.18em] text-zinc-400 mb-1">
                    Current vehicle
                  </p>
                  <p className="text-lg font-semibold text-white">
                    Your SIXT car
                  </p>
                </div>
                <div className="flex flex-col items-end gap-1">
                  <span
                    className={`inline-flex items-center rounded-full px-2.5 py-1 text-[10px] font-medium ${
                      doorsLocked
                        ? "bg-emerald-500/15 text-emerald-300 border border-emerald-400/40"
                        : doorsLocked === false
                        ? "bg-yellow-500/10 text-yellow-300 border border-yellow-400/40"
                        : "bg-zinc-800 text-zinc-300 border border-zinc-700"
                    }`}
                  >
                    <span
                      className={`mr-1 h-1.5 w-1.5 rounded-full ${
                        doorsLocked
                          ? "bg-emerald-400"
                          : doorsLocked === false
                          ? "bg-yellow-300"
                          : "bg-zinc-500"
                      }`}
                    />
                    {doorsLocked === true && "Locked"}
                    {doorsLocked === false && "Unlocked"}
                    {doorsLocked === null && "Status unknown"}
                  </span>
                  {isBusy && (
                    <span className="text-[10px] text-zinc-400">
                      {action === "locking" && "Locking doors…"}
                      {action === "unlocking" && "Unlocking door…"}
                      {action === "blinking" && "Blinking lights…"}
                    </span>
                  )}
                </div>
              </div>

              <div className="mt-3 h-16 rounded-xl border border-zinc-800 bg-zinc-900/60 flex items-center justify-center text-[11px] text-zinc-400 font-medium tracking-wide">
                Remote access enabled
              </div>
            </div>
          </div>
        </div>

        {/* Main controls */}
        <div className="flex gap-3 mb-5">
          {/* Lock */}
          <button
            onClick={handleLock}
            disabled={isBusy || !bookingId}
            className={`group flex-1 flex flex-col items-center justify-center rounded-2xl py-4 sm:py-5 text-center transition-all duration-200
              ${
                isBusy || !bookingId
                  ? "bg-orange-500/30 text-black/60 cursor-not-allowed"
                  : "bg-gradient-to-b from-orange-400 to-orange-600 text-black shadow-[0_10px_25px_rgba(248,113,113,0.55)] hover:shadow-[0_16px_35px_rgba(248,113,113,0.7)] hover:translate-y-0.5 active:scale-[0.98]"
              }
              ${
                doorsLocked
                  ? "ring-2 ring-orange-300/70 ring-offset-0"
                  : "ring-0"
              }
            `}
          >
            <div className="relative mb-2">
              <Lock
                className={`w-6 h-6 sm:w-7 sm:h-7 ${
                  isLocking ? "animate-pulse" : ""
                }`}
              />
            </div>
            <span className="text-sm sm:text-base font-semibold">
              Lock
            </span>
            <span className="text-[11px] mt-1 opacity-80">
              All doors
            </span>
          </button>

          {/* Unlock */}
          <button
            onClick={handleUnlock}
            disabled={isBusy || !bookingId}
            className={`flex-1 flex flex-col items-center justify-center rounded-2xl py-4 sm:py-5 text-center transition-all duration-200 border
              ${
                isBusy || !bookingId
                  ? "bg-zinc-900/80 border-zinc-700 text-zinc-500 cursor-not-allowed"
                  : "bg-zinc-900/80 border-zinc-700 text-zinc-100 hover:border-orange-400 hover:bg-zinc-900 hover:translate-y-0.5 active:scale-[0.98]"
              }
              ${
                doorsLocked === false
                  ? "ring-2 ring-orange-300/70 ring-offset-0"
                  : "ring-0"
              }
            `}
          >
            <Unlock
              className={`w-6 h-6 sm:w-7 sm:h-7 mb-2 ${
                isUnlocking ? "animate-pulse" : ""
              }`}
            />
            <span className="text-sm sm:text-base font-semibold">
              Unlock
            </span>
            <span className="text-[11px] mt-1 text-zinc-400">
              Driver door
            </span>
          </button>
        </div>

        {/* Blink */}
        <button
          onClick={handleBlink}
          disabled={isBusy || !bookingId}
          className={`w-full flex items-center justify-center gap-2 rounded-2xl py-3.5 text-sm font-medium transition-all duration-200 border
            ${
              isBusy || !bookingId
                ? "bg-zinc-900/80 border-zinc-800 text-zinc-500 cursor-not-allowed"
                : "bg-zinc-900/90 border-zinc-700 text-zinc-100 hover:border-orange-400 hover:bg-zinc-900 hover:translate-y-0.5 active:scale-[0.98]"
            }
            ${isBlinking ? "ring-2 ring-orange-300/70" : ""}
          `}
        >
          <Bell
            className={`w-4 h-4 ${
              isBlinking ? "animate-pulse" : ""
            }`}
          />
          <span>Blink · Lights & horn</span>
        </button>

        {/* Messages */}
        {(message || error) && (
          <div className="mt-4 text-xs sm:text-sm">
            {message && (
              <p className="text-emerald-400 font-medium">{message}</p>
            )}
            {error && <p className="text-red-400 font-medium">{error}</p>}
          </div>
        )}

        {bookingId && (
          <p className="mt-4 text-[11px] text-zinc-500 text-right">
            Booking ID: <span className="font-mono">{bookingId}</span>
          </p>
        )}
      </div>
    </div>
  );
}
