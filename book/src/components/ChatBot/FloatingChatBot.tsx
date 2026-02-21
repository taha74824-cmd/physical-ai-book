import React, { useState, useEffect } from "react";
import ChatBot from "./index";
import styles from "./FloatingChatBot.module.css";

export default function FloatingChatBot() {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedText, setSelectedText] = useState("");
  const [showSelectionTooltip, setShowSelectionTooltip] = useState(false);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleSelectionChange = () => {
      const selection = window.getSelection();
      if (!selection || selection.isCollapsed) {
        setShowSelectionTooltip(false);
        return;
      }

      const text = selection.toString().trim();
      if (text.length < 20) {
        setShowSelectionTooltip(false);
        return;
      }

      // Get selection position
      const range = selection.getRangeAt(0);
      const rect = range.getBoundingClientRect();

      setTooltipPos({
        x: rect.left + rect.width / 2,
        y: rect.top - 10 + window.scrollY,
      });
      setShowSelectionTooltip(true);
    };

    document.addEventListener("selectionchange", handleSelectionChange);
    return () => document.removeEventListener("selectionchange", handleSelectionChange);
  }, []);

  const handleAskAboutSelection = () => {
    const selection = window.getSelection();
    if (selection) {
      const text = selection.toString().trim();
      setSelectedText(text);
      setIsOpen(true);
      setShowSelectionTooltip(false);
      selection.removeAllRanges();
    }
  };

  return (
    <>
      {/* Selection tooltip */}
      {showSelectionTooltip && (
        <div
          className={styles.selectionTooltip}
          style={{ left: tooltipPos.x, top: tooltipPos.y }}
        >
          <button
            className={styles.askBtn}
            onClick={handleAskAboutSelection}
            onMouseDown={(e) => e.preventDefault()} // Prevent selection loss
          >
            🤖 Ask AI about this
          </button>
        </div>
      )}

      {/* Floating chat panel */}
      {isOpen && (
        <div className={styles.floatingPanel}>
          <ChatBot
            initialSelectedText={selectedText}
            onClose={() => {
              setIsOpen(false);
              setSelectedText("");
            }}
            embedded={true}
          />
        </div>
      )}

      {/* Floating button */}
      {!isOpen && (
        <button
          className={styles.floatingBtn}
          onClick={() => setIsOpen(true)}
          title="Ask the AI Assistant"
        >
          <span className={styles.btnIcon}>🤖</span>
          <span className={styles.btnLabel}>Ask AI</span>
        </button>
      )}
    </>
  );
}
