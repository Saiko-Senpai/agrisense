"use client";

import { useSearchParams } from "next/navigation";
import Chatbot from "@/components/chatbot/Chatbot";

export default function AssistantClient() {
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get("q") ?? undefined;
  return <Chatbot initialQuery={initialQuery} />;
}
