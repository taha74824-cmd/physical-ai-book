import React from "react";
import FloatingChatBot from "@site/src/components/ChatBot/FloatingChatBot";

// Root component wraps every page — perfect for global components
export default function Root({ children }: { children: React.ReactNode }) {
  return (
    <>
      {children}
      <FloatingChatBot />
    </>
  );
}
