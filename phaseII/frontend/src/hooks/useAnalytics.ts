/**
 * Analytics tracking hook (T072, FR-036)
 *
 * Provides utilities for tracking user interaction events.
 * Respects user consent and privacy settings (FR-038, FR-039).
 */

import { useCallback, useEffect, useState } from 'react';

interface AnalyticsEvent {
  event_name: string;
  properties?: Record<string, any>;
}

interface AnalyticsConfig {
  enabled: boolean;
  consent: boolean;
}

// Storage key for analytics consent
const ANALYTICS_CONSENT_KEY = 'analytics_consent';

/**
 * Get analytics consent from local storage
 */
function getAnalyticsConsent(): boolean {
  if (typeof window === 'undefined') return false;

  const consent = localStorage.getItem(ANALYTICS_CONSENT_KEY);
  // Default to true if not set (opt-out model per FR-039)
  return consent !== 'false';
}

/**
 * Set analytics consent in local storage
 */
function setAnalyticsConsent(consent: boolean): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(ANALYTICS_CONSENT_KEY, String(consent));
}

/**
 * Send analytics event to backend
 */
async function sendEvent(event: AnalyticsEvent): Promise<void> {
  try {
    // Don't send in development (FR-040)
    if (process.env.NODE_ENV === 'development') {
      console.log('[Analytics Event]', event);
      return;
    }

    // Send to analytics endpoint
    await fetch('/api/analytics/events', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(event),
      // Use keepalive to ensure event is sent even if user navigates away
      keepalive: true,
    }).catch(() => {
      // Silently fail - don't block user experience
    });
  } catch (error) {
    // Silently fail - analytics should never break the app
  }
}

/**
 * Hook for tracking analytics events
 */
export function useAnalytics() {
  const [config, setConfig] = useState<AnalyticsConfig>({
    enabled: true,
    consent: getAnalyticsConsent(),
  });

  // Track event with consent check
  const track = useCallback(
    (eventName: string, properties?: Record<string, any>) => {
      // Check consent (FR-039)
      if (!config.consent || !config.enabled) {
        return;
      }

      // Validate no PII in properties (FR-038)
      // This is a client-side check - backend also validates
      const sanitizedProperties = properties ? { ...properties } : {};

      // Remove any keys that might contain PII
      const piiKeys = ['email', 'name', 'phone', 'address', 'password'];
      piiKeys.forEach(key => {
        if (key in sanitizedProperties) {
          delete sanitizedProperties[key];
        }
      });

      sendEvent({
        event_name: eventName,
        properties: sanitizedProperties,
      });
    },
    [config.consent, config.enabled]
  );

  // Opt out of analytics (FR-039)
  const optOut = useCallback(() => {
    setAnalyticsConsent(false);
    setConfig(prev => ({ ...prev, consent: false }));
  }, []);

  // Opt in to analytics
  const optIn = useCallback(() => {
    setAnalyticsConsent(true);
    setConfig(prev => ({ ...prev, consent: true }));
  }, []);

  // Check if user has consented
  const hasConsent = config.consent;

  return {
    track,
    optOut,
    optIn,
    hasConsent,
    enabled: config.enabled,
  };
}

/**
 * Pre-defined event tracking functions for common actions (FR-036)
 */
export function useTaskAnalytics() {
  const { track } = useAnalytics();

  return {
    /**
     * Track task creation event
     */
    trackTaskCreated: useCallback(
      (taskData?: { priority?: string; has_due_date?: boolean; has_tags?: boolean }) => {
        track('task_created', {
          priority: taskData?.priority,
          has_due_date: taskData?.has_due_date,
          has_tags: taskData?.has_tags,
          timestamp: new Date().toISOString(),
        });
      },
      [track]
    ),

    /**
     * Track task completion event
     */
    trackTaskCompleted: useCallback(
      (taskData?: { time_to_complete?: number; had_reminder?: boolean }) => {
        track('task_completed', {
          time_to_complete_seconds: taskData?.time_to_complete,
          had_reminder: taskData?.had_reminder,
          timestamp: new Date().toISOString(),
        });
      },
      [track]
    ),

    /**
     * Track reminder set event
     */
    trackReminderSet: useCallback(
      (reminderData?: { timing?: string; channel?: string }) => {
        track('reminder_set', {
          timing: reminderData?.timing,
          channel: reminderData?.channel,
          timestamp: new Date().toISOString(),
        });
      },
      [track]
    ),

    /**
     * Track search performed event
     */
    trackSearchPerformed: useCallback(
      (searchData?: { query_length?: number; has_filters?: boolean }) => {
        track('search_performed', {
          query_length: searchData?.query_length,
          has_filters: searchData?.has_filters,
          timestamp: new Date().toISOString(),
        });
      },
      [track]
    ),

    /**
     * Track task deleted event
     */
    trackTaskDeleted: useCallback(
      (taskData?: { was_completed?: boolean; had_reminder?: boolean }) => {
        track('task_deleted', {
          was_completed: taskData?.was_completed,
          had_reminder: taskData?.had_reminder,
          timestamp: new Date().toISOString(),
        });
      },
      [track]
    ),

    /**
     * Track drag and drop reorder event
     */
    trackTaskReordered: useCallback(
      (reorderData?: { task_count?: number; moved_positions?: number }) => {
        track('task_reordered', {
          task_count: reorderData?.task_count,
          moved_positions: reorderData?.moved_positions,
          timestamp: new Date().toISOString(),
        });
      },
      [track]
    ),
  };
}
