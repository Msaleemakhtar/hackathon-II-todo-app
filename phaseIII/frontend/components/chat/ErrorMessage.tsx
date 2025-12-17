"use client";

/**
 * T099: ErrorMessage Component with retry button
 *
 * Displays user-friendly error messages with:
 * - Clear error description
 * - Suggested actions
 * - Retry button
 * - Dismiss functionality
 */

interface ErrorMessageProps {
  error: string | { detail: string; code?: string; suggestions?: string[] };
  onRetry?: () => void;
  onDismiss?: () => void;
}

export default function ErrorMessage({ error, onRetry, onDismiss }: ErrorMessageProps) {
  // Parse error object or string
  const errorDetails = typeof error === "string"
    ? { detail: error, code: undefined, suggestions: [] }
    : error;

  const { detail, code, suggestions = [] } = errorDetails;

  // Determine error severity by code
  const getSeverityStyles = () => {
    if (code === "UNAUTHORIZED" || code === "FORBIDDEN") {
      return { bg: "#fff3e0", color: "#e65100", border: "#ff9800" };
    }
    if (code === "AI_SERVICE_UNAVAILABLE") {
      return { bg: "#e1f5fe", color: "#01579b", border: "#03a9f4" };
    }
    // Default error
    return { bg: "#ffebee", color: "#c62828", border: "#f44336" };
  };

  const styles = getSeverityStyles();

  return (
    <div style={{
      padding: "1rem",
      backgroundColor: styles.bg,
      borderLeft: `4px solid ${styles.border}`,
      borderRadius: "4px",
      marginBottom: "1rem",
    }}>
      {/* Error Header */}
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: "bold", color: styles.color, marginBottom: "0.5rem" }}>
            {code ? `Error: ${code}` : "Error"}
          </div>
          <div style={{ color: styles.color, fontSize: "0.875rem", whiteSpace: "pre-wrap" }}>
            {detail}
          </div>
        </div>

        {/* Dismiss button */}
        {onDismiss && (
          <button
            onClick={onDismiss}
            style={{
              background: "none",
              border: "none",
              color: styles.color,
              cursor: "pointer",
              fontSize: "1.25rem",
              padding: "0 0.5rem",
              marginLeft: "0.5rem",
            }}
            title="Dismiss"
          >
            ×
          </button>
        )}
      </div>

      {/* Suggestions */}
      {suggestions.length > 0 && (
        <div style={{ marginTop: "0.75rem", fontSize: "0.8125rem" }}>
          <div style={{ fontWeight: "600", color: styles.color, marginBottom: "0.25rem" }}>
            Suggestions:
          </div>
          <ul style={{ margin: "0", paddingLeft: "1.25rem", color: styles.color }}>
            {suggestions.map((suggestion, index) => (
              <li key={index} style={{ marginBottom: "0.125rem" }}>
                {suggestion}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Retry button */}
      {onRetry && (
        <div style={{ marginTop: "0.75rem" }}>
          <button
            onClick={onRetry}
            style={{
              padding: "0.5rem 1rem",
              backgroundColor: styles.border,
              color: "#fff",
              border: "none",
              borderRadius: "4px",
              fontSize: "0.875rem",
              cursor: "pointer",
              fontWeight: "500",
            }}
          >
            🔄 Retry
          </button>
        </div>
      )}
    </div>
  );
}
