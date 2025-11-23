import { FormEvent, useEffect, useRef, useState } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useLocation, useNavigate } from "react-router-dom";
import api from "@/api/api";

type ChatMessage = {
  id: number;
  role: "user" | "assistant";
  content: string;
};

type ChatbotProps = {
  onAiUpdate?: (data: any) => void; // you can type this as ChatApiResponse if you like
};

export default function Chatbot({ onAiUpdate }: ChatbotProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 1,
      role: "assistant",
      content: "Hi! What kind of car do you want to rent today?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);

  const bottomRef = useRef<HTMLDivElement | null>(null);

  const location = useLocation();
  const navigate = useNavigate();
  const chatSessionId = (location.state as { chatSessionId?: string } | null)
    ?.chatSessionId;

  // If for some reason there's no chatSessionId, send user back to login
  useEffect(() => {
    if (!chatSessionId) {
      navigate("/", { replace: true });
    }
  }, [chatSessionId, navigate]);

  // auto-scroll to latest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text || isSending || !chatSessionId) return;

    const userMessage: ChatMessage = {
      id: Date.now(),
      role: "user",
      content: text,
    };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput("");
    setIsSending(true);

    try {
      const res = await api.post("/api/ai-engine/chat/", {
        chat_session_id: chatSessionId,
        message: text,
        messages: updatedMessages.map((m) => ({
          role: m.role,
          content: m.content,
        })),
      });

      const data = res.data;

      // ⬆️ Send cars/protections/addons up to HomePage
      if (onAiUpdate) {
        onAiUpdate(data);
      }

      // ⬇️ Chat UI: append last assistant message
      const lastAssistant = [...data.messages]
        .reverse()
        .find((m: any) => m.role === "assistant");

      if (lastAssistant) {
        const botMessage: ChatMessage = {
          id: Date.now() + 1,
          role: "assistant",
          content: lastAssistant.content,
        };

        setMessages((prev) => [...prev, botMessage]);
      }
    } catch (err) {
      console.error(err);
      const errorMessage: ChatMessage = {
        id: Date.now() + 2,
        role: "assistant",
        content:
          "Sorry, something went wrong while contacting the server. Please try again.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsSending(false);
    }
  }

  return (
    <Card className="w-full max-w-lg h-[80vh] flex flex-col rounded-2xl shadow-md">
      <CardHeader>
        <CardTitle className="text-lg font-semibold">SixtSense</CardTitle>
      </CardHeader>

      <CardContent className="flex-1 px-4">
        <ScrollArea className="h-full pr-2">
          <div className="flex flex-col gap-3">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                {msg.role === "assistant" && (
                  <Avatar className="mr-2 h-7 w-7">
                    <AvatarImage src="logo.png" alt="Bot" />
                    <AvatarFallback>AI</AvatarFallback>
                  </Avatar>
                )}

                <div
                  className={`rounded-2xl px-3 py-2 text-sm max-w-[80%] ${
                    msg.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted-foreground/10 text-foreground"
                  }`}
                >
                  {msg.content}
                </div>

                {msg.role === "user" && (
                  <Avatar className="ml-2 h-7 w-7">
                    <AvatarImage src="" alt="You" />
                    <AvatarFallback>U</AvatarFallback>
                  </Avatar>
                )}
              </div>
            ))}

            <div ref={bottomRef} />
          </div>
        </ScrollArea>
      </CardContent>

      <CardFooter className="border-t px-4 py-3">
        <form onSubmit={handleSubmit} className="flex w-full gap-2">
          <Input
            placeholder="Type a message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isSending}
          />
          <Button type="submit" disabled={isSending || !chatSessionId}>
            {isSending ? "Sending..." : "Send"}
          </Button>
        </form>
      </CardFooter>
    </Card>
  );
}
