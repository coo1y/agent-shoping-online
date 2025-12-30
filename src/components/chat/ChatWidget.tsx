"use client";

import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useCart } from "@/components/providers/CartProvider";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageCircle, X, Send, Bot, User } from "lucide-react";
import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";

type Message = {
  role: "user" | "assistant";
  content: string;
};

export function ChatWidget() {
  const router = useRouter();
  const { addItem, removeItem, updateQuantity, items } = useCart();
  const [isOpen, setIsOpen] = useState(false);
  const [sessionId, setSessionId] = useState("default_session");
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: "Hi! I'm your AI shopping assistant. How can I help you find the perfect gear today?" },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isOpen]);

  useEffect(() => {
    const storageKey = "techshop_session_id";
    const existing = localStorage.getItem(storageKey);
    if (existing) {
      setSessionId(existing);
      return;
    }

    const newId =
      globalThis.crypto?.randomUUID?.() ??
      `session_${Math.random().toString(16).slice(2)}_${Date.now()}`;
    localStorage.setItem(storageKey, newId);
    setSessionId(newId);
  }, []);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = { role: "user", content: inputValue };
    // Create a local copy of messages to send, including the new one
    const newMessages = [...messages, userMessage];
    
    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);
    const startTime = Date.now();

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          messages: newMessages,
          session_id: sessionId,
          cart: items,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      if (!response.body) throw new Error("No response body");

      // Prepare for streaming
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let accumulatedContent = "";
      let isFirstChunk = true;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        accumulatedContent += chunk;

        // Process any complete JSON blocks found in the content
        // We use a loop to handle multiple blocks if they arrive in the same chunk
        // Note: We strip the blocks from accumulatedContent so they are not displayed
        
        let foundMatch = true;
        while (foundMatch) {
            foundMatch = false;
            // Use non-global regex to find the first match, extract it, and remove it
            const singleRegex = /```json\s*([\s\S]*?)\s*```/;
            const m = accumulatedContent.match(singleRegex);
            
            if (m) {
                foundMatch = true;
                const fullMatch = m[0];
                const jsonStr = m[1];
                
                console.log("ChatWidget: Processing JSON block:", jsonStr);
                try {
                    const actionData = JSON.parse(jsonStr);
                    console.log("ChatWidget: Parsed Action:", actionData);
                    
                    if (actionData.action === "navigate" && actionData.target) {
                        router.push(actionData.target);
                    } else if (actionData.action === "add_to_cart" && actionData.added_item) {
                        addItem(actionData.added_item);
                    } else if (actionData.action === "remove_from_cart" && actionData.product_id) {
                        console.log("ChatWidget: Removing item", actionData.product_id);
                        removeItem(actionData.product_id);
                    } else if (actionData.action === "update_cart_quantity" && actionData.product_id) {
                        // Handle quantity safely (it might be a string or number)
                        const qty = Number(actionData.quantity);
                        if (!isNaN(qty)) {
                             console.log("ChatWidget: Updating quantity", actionData.product_id, qty);
                             updateQuantity(actionData.product_id, qty);
                        } else {
                             console.error("ChatWidget: Invalid quantity for update", actionData.quantity);
                        }
                    } else {
                        console.warn("ChatWidget: Unknown or incomplete action", actionData);
                    }
                } catch (e) {
                    console.error("Failed to parse action JSON", e);
                }
                
                // Remove this block from accumulatedContent so it's not processed again
                // and not displayed
                accumulatedContent = accumulatedContent.replace(fullMatch, "").trim();
            }
        }

        // Only update UI if we have actual content to show
        if (accumulatedContent.trim()) {
            if (isFirstChunk) {
                // Ensure "Thinking..." state is visible for at least 2s (2000ms) to ensure the user sees it
                const elapsedTime = Date.now() - startTime;
                if (elapsedTime < 2000) {
                    await new Promise(resolve => setTimeout(resolve, 2000 - elapsedTime));
                }

                setIsLoading(false); // Stop loading spinner as we start showing text
                const assistantMessage: Message = { role: "assistant", content: accumulatedContent };
                setMessages((prev) => [...prev, assistantMessage]);
                isFirstChunk = false;
            } else {
                setMessages((prev) => {
                    const updatedMessages = [...prev];
                    const lastMsg = updatedMessages[updatedMessages.length - 1];
                    if (lastMsg.role === "assistant") {
                        lastMsg.content = accumulatedContent;
                    }
                    return updatedMessages;
                });
            }
        }
      }

    } catch (error) {
      console.error("Error sending message:", error);
      // Only add error message if we haven't started streaming (isLoading is still true)
      // or if we want to show error anyway.
      // If we failed mid-stream, the partial message is already there.
      if (isLoading) {
          setMessages((prev) => [
            ...prev,
            { role: "assistant", content: "Sorry, I'm having trouble connecting to the server right now." },
          ]);
      }
    } finally {
      // Ensure "Thinking..." state is visible for at least 1.5s to prevent flickering
      // This covers cases where the request fails or returns non-text content quickly
      const elapsedTime = Date.now() - startTime;
      if (elapsedTime < 1500) {
          await new Promise(resolve => setTimeout(resolve, 1500 - elapsedTime));
      }
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-4">
      {isOpen && (
        <Card className="w-[450px] h-[700px] flex flex-col shadow-2xl border-0 ring-1 ring-black/5 animate-in slide-in-from-bottom-5 duration-300 rounded-3xl overflow-hidden bg-white/95 backdrop-blur-md font-sans">
          {/* Header */}
          <CardHeader className="flex flex-row items-center justify-between space-y-0 p-6 border-b bg-gradient-to-br from-orange-400 via-primary to-orange-500 text-primary-foreground relative overflow-hidden">
            <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 brightness-100 contrast-150 mix-blend-soft-light" />
            <div className="absolute -top-10 -right-10 w-32 h-32 bg-white/10 blur-3xl rounded-full pointer-events-none" />
            <div className="absolute -bottom-10 -left-10 w-32 h-32 bg-black/5 blur-3xl rounded-full pointer-events-none" />
            
            <div className="flex items-center gap-4 relative z-10">
              <div className="h-11 w-11 rounded-full bg-white/20 backdrop-blur-md flex items-center justify-center shadow-[inset_0_0_0_1px_rgba(255,255,255,0.2)] ring-1 ring-black/5">
                <Bot className="h-6 w-6 text-white drop-shadow-sm" />
              </div>
              <div className="flex flex-col gap-0.5">
                <CardTitle className="text-xl font-bold tracking-tight text-white drop-shadow-sm">TechWise: Intelligent Helper</CardTitle>
                <div className="flex items-center gap-1.5 bg-black/10 px-2 py-0.5 rounded-full w-fit backdrop-blur-sm">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-300 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-green-400 shadow-[0_0_5px_rgba(74,222,128,0.5)]"></span>
                  </span>
                  <p className="text-[10px] font-semibold text-white/90 uppercase tracking-wider">Online</p>
                </div>
              </div>
            </div>
            <Button variant="ghost" size="icon" className="h-9 w-9 text-white hover:bg-white/20 rounded-full relative z-10 transition-colors" onClick={() => setIsOpen(false)}>
              <X className="h-5 w-5" />
            </Button>
          </CardHeader>

          {/* Chat Area */}
          <CardContent className="flex-1 p-0 overflow-hidden bg-gray-50/50 relative">
             {/* Background decorative elements */}
            <div className="absolute inset-0 opacity-[0.03] pointer-events-none" style={{ backgroundImage: "radial-gradient(#000 1px, transparent 1px)", backgroundSize: "20px 20px" }} />
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] bg-primary/5 blur-[100px] rounded-full pointer-events-none" />
            
            <ScrollArea className="h-full px-4 py-6">
              <div className="flex flex-col gap-6">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={cn(
                      "flex w-full gap-3",
                      message.role === "user" ? "flex-row-reverse" : "flex-row"
                    )}
                  >
                    {/* Avatar */}
                    <div className={cn(
                      "flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center shadow-sm ring-1 ring-black/5",
                      message.role === "user" 
                        ? "bg-white text-primary" 
                        : "bg-gradient-to-br from-primary to-orange-600 text-white"
                    )}>
                      {message.role === "user" ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                    </div>

                    {/* Message Bubble */}
                    <div
                      className={cn(
                        "flex flex-col gap-1 max-w-[80%] px-5 py-3.5 text-sm shadow-sm relative",
                        message.role === "user"
                          ? "bg-gradient-to-br from-primary to-orange-600 text-white rounded-2xl rounded-tr-sm"
                          : "bg-white text-gray-800 border border-gray-100 rounded-2xl rounded-tl-sm"
                      )}
                    >
                      <ReactMarkdown
                        components={{
                          p: ({ children }) => <p className="mb-2 last:mb-0 leading-relaxed">{children}</p>,
                          ul: ({ children }) => <ul className="list-disc pl-4 mb-2 space-y-1">{children}</ul>,
                          ol: ({ children }) => <ol className="list-decimal pl-4 mb-2 space-y-1">{children}</ol>,
                          li: ({ children }) => <li className="leading-relaxed">{children}</li>,
                          strong: ({ children }) => <span className="font-bold">{children}</span>,
                        }}
                      >
                        {message.content}
                      </ReactMarkdown>
                    </div>
                  </div>
                ))}
                
                {isLoading && (
                   <div className="flex w-full gap-3">
                    <div className="flex-shrink-0 h-8 w-8 rounded-full bg-gradient-to-br from-primary to-orange-600 text-white flex items-center justify-center shadow-sm ring-1 ring-black/5">
                      <Bot className="h-4 w-4" />
                    </div>
                    <div className="flex w-max flex-col gap-2 rounded-2xl rounded-tl-sm px-5 py-4 text-sm bg-white border border-gray-100 shadow-sm">
                      <div className="flex items-center gap-2.5">
                          <span className="text-muted-foreground text-xs font-medium animate-pulse">Thinking</span>
                          <div className="flex items-center gap-1 h-3">
                              <span className="w-1.5 h-1.5 bg-primary/60 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                              <span className="w-1.5 h-1.5 bg-primary/60 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                              <span className="w-1.5 h-1.5 bg-primary/60 rounded-full animate-bounce"></span>
                          </div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={scrollRef} />
              </div>
            </ScrollArea>
          </CardContent>

          {/* Input Area */}
          <CardFooter className="p-4 border-t bg-white/80 backdrop-blur-lg">
            <div className="flex w-full items-end gap-2 bg-white rounded-[24px] border border-gray-200 pl-4 pr-2 py-2 focus-within:ring-2 focus-within:ring-primary/20 focus-within:border-primary transition-all shadow-sm hover:shadow-md hover:border-gray-300">
              <Input
                placeholder="Ask about products..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={isLoading}
                className="border-none shadow-none focus-visible:ring-0 bg-transparent h-auto py-2.5 px-0 text-gray-800 placeholder:text-gray-400 min-h-[44px] text-[15px]"
              />
              <Button 
                size="icon" 
                className={cn(
                  "h-10 w-10 rounded-full shrink-0 transition-all duration-300 shadow-sm",
                  inputValue.trim() 
                    ? "bg-gradient-to-r from-primary to-orange-500 text-white hover:shadow-lg hover:scale-105 active:scale-95" 
                    : "bg-gray-100 text-gray-400 cursor-not-allowed"
                )}
                onClick={handleSendMessage} 
                disabled={isLoading || !inputValue.trim()}
              >
                <Send className="h-5 w-5 ml-0.5" />
              </Button>
            </div>
          </CardFooter>
        </Card>
      )}
      
      {!isOpen && (
        <Button
          onClick={() => setIsOpen(true)}
          size="lg"
          className="rounded-full h-16 w-16 shadow-2xl hover:shadow-primary/25 hover:scale-110 transition-all duration-300 bg-gradient-to-r from-primary to-primary/90 text-primary-foreground border-4 border-white/10"
        >
          <MessageCircle className="h-8 w-8" />
          <span className="absolute top-0 right-0 flex h-4 w-4">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-4 w-4 bg-red-500 border-2 border-white"></span>
          </span>
        </Button>
      )}
    </div>
  );
}
