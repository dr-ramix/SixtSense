import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import api from "@/api/api";

export default function MainPage() {
  const [bookingId, setBookingId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const response = await api.post("/api/ai-engine/start/", {
        booking_id: bookingId,
      });

      const chatSessionId = response.data.chat_session_id;

      console.log("Chat session created:", response.data);

      navigate("/home", {
        state: { chatSessionId },
      });
    } catch (err: any) {
      console.error(err);
      setError(
        err?.response?.data?.detail ||
          "Could not start chat session. Please check the booking ID."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-black via-zinc-900 to-orange-600 p-4">
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-md"
      >
        <Card className="shadow-2xl rounded-3xl border border-orange-500/40 bg-black/90 backdrop-blur">
          <CardContent className="p-8 space-y-6">
            <div className="text-center space-y-2">
              <p className="text-xs tracking-[0.25em] text-orange-400 font-semibold uppercase">
                SIXT • AI ASSISTANT
              </p>
              <h1 className="text-3xl font-extrabold text-white">
                Welcome to SixtSense
              </h1>
              <p className="text-sm text-zinc-300">
                Enter your <strong>booking ID</strong> and press the button to
                start your upgrade session.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <label className="block text-sm font-medium text-zinc-200">
                  Booking ID
                </label>
                <Input
                  value={bookingId}
                  onChange={(e) => setBookingId(e.target.value)}
                  placeholder="e.g. AB1234567"
                  required
                  className="bg-zinc-900/70 border-zinc-700 text-zinc-100 placeholder:text-zinc-500"
                  disabled={loading}
                />
              </div>

              {error && (
                <div className="text-sm text-red-400 bg-red-900/20 border border-red-500/40 rounded-xl px-3 py-2">
                  {error}
                </div>
              )}

              <Button
                type="submit"
                disabled={loading || !bookingId}
                className="w-full rounded-2xl py-2.5 bg-[#f97316]! hover:bg-[#ea580c]! focus-visible:ring-[#f97316] focus-visible:ring-offset-2 focus-visible:ring-offset-black text-black shadow-lg shadow-orange-500/40 font-semibold transition-colors disabled:bg-[#f97316]/60 disabled:text-black"
              >
                {loading ? "Starting..." : "Start AI Upgrade Session"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
