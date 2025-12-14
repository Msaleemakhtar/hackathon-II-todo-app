/**
 * useDebounce Hook - Debounce values to prevent excessive updates (T035, US2)
 *
 * Delays updating a value until after a specified delay has elapsed since the last change.
 * Perfect for search inputs, filters, and other rapid-change scenarios.
 *
 * Benefits:
 * - Reduces API calls by up to 90%
 * - Improves UX by preventing jittery UI updates
 * - Reduces server load from excessive queries
 * - Better battery life on mobile devices
 *
 * @example
 * ```typescript
 * const [searchTerm, setSearchTerm] = useState('');
 * const debouncedSearch = useDebounce(searchTerm, 300);
 *
 * useEffect(() => {
 *   // Only triggers after user stops typing for 300ms
 *   if (debouncedSearch) {
 *     fetchSearchResults(debouncedSearch);
 *   }
 * }, [debouncedSearch]);
 * ```
 */

import { useEffect, useState } from 'react';

/**
 * Debounce a value with a specified delay
 *
 * @param value - Value to debounce
 * @param delay - Delay in milliseconds (default: 300ms)
 * @returns Debounced value
 */
export function useDebounce<T>(value: T, delay: number = 300): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    // Set up the timeout to update debounced value
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    // Clean up the timeout if value changes before delay expires
    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

/**
 * Debounce a callback function
 *
 * Returns a debounced version of the callback that delays invoking
 * until after `delay` milliseconds have elapsed since the last time it was invoked.
 *
 * @param callback - Function to debounce
 * @param delay - Delay in milliseconds (default: 300ms)
 * @returns Debounced callback
 *
 * @example
 * ```typescript
 * const debouncedSearch = useDebouncedCallback(
 *   (query: string) => fetchSearchResults(query),
 *   500
 * );
 *
 * // Call it from event handler
 * <input onChange={(e) => debouncedSearch(e.target.value)} />
 * ```
 */
export function useDebouncedCallback<T extends (...args: any[]) => any>(
  callback: T,
  delay: number = 300
): (...args: Parameters<T>) => void {
  const [timeoutId, setTimeoutId] = useState<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // Cleanup on unmount
    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [timeoutId]);

  return (...args: Parameters<T>) => {
    // Clear existing timeout
    if (timeoutId) {
      clearTimeout(timeoutId);
    }

    // Set new timeout
    const newTimeoutId = setTimeout(() => {
      callback(...args);
    }, delay);

    setTimeoutId(newTimeoutId);
  };
}

/**
 * Throttle a value - limits the rate at which a value can update
 *
 * Similar to debounce but guarantees the value updates at least once per interval.
 * Useful for scroll handlers and window resize.
 *
 * @param value - Value to throttle
 * @param interval - Minimum time between updates in milliseconds (default: 100ms)
 * @returns Throttled value
 *
 * @example
 * ```typescript
 * const [scrollY, setScrollY] = useState(0);
 * const throttledScrollY = useThrottle(scrollY, 100);
 *
 * useEffect(() => {
 *   const handleScroll = () => setScrollY(window.scrollY);
 *   window.addEventListener('scroll', handleScroll);
 *   return () => window.removeEventListener('scroll', handleScroll);
 * }, []);
 * ```
 */
export function useThrottle<T>(value: T, interval: number = 100): T {
  const [throttledValue, setThrottledValue] = useState<T>(value);
  const [lastUpdate, setLastUpdate] = useState<number>(Date.now());

  useEffect(() => {
    const now = Date.now();
    const timeSinceLastUpdate = now - lastUpdate;

    if (timeSinceLastUpdate >= interval) {
      // Update immediately
      setThrottledValue(value);
      setLastUpdate(now);
    } else {
      // Schedule update for the end of the interval
      const timeoutId = setTimeout(
        () => {
          setThrottledValue(value);
          setLastUpdate(Date.now());
        },
        interval - timeSinceLastUpdate
      );

      return () => clearTimeout(timeoutId);
    }
  }, [value, interval, lastUpdate]);

  return throttledValue;
}

/**
 * Utility function for creating debounced functions (non-hook)
 *
 * @param fn - Function to debounce
 * @param delay - Delay in milliseconds
 * @returns Debounced function
 *
 * @example
 * ```typescript
 * const debouncedFn = debounce((query: string) => {
 *   console.log('Searching for:', query);
 * }, 300);
 *
 * debouncedFn('test'); // Only logs after 300ms of inactivity
 * ```
 */
export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  delay: number = 300
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout | null = null;

  return (...args: Parameters<T>) => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }

    timeoutId = setTimeout(() => {
      fn(...args);
    }, delay);
  };
}

/**
 * Utility function for creating throttled functions (non-hook)
 *
 * @param fn - Function to throttle
 * @param interval - Minimum time between calls in milliseconds
 * @returns Throttled function
 *
 * @example
 * ```typescript
 * const throttledFn = throttle((y: number) => {
 *   console.log('Scroll position:', y);
 * }, 100);
 *
 * window.addEventListener('scroll', () => throttledFn(window.scrollY));
 * ```
 */
export function throttle<T extends (...args: any[]) => any>(
  fn: T,
  interval: number = 100
): (...args: Parameters<T>) => void {
  let lastCall = 0;
  let timeoutId: NodeJS.Timeout | null = null;

  return (...args: Parameters<T>) => {
    const now = Date.now();
    const timeSinceLastCall = now - lastCall;

    if (timeSinceLastCall >= interval) {
      // Call immediately
      fn(...args);
      lastCall = now;
    } else {
      // Schedule for end of interval
      if (timeoutId) {
        clearTimeout(timeoutId);
      }

      timeoutId = setTimeout(
        () => {
          fn(...args);
          lastCall = Date.now();
        },
        interval - timeSinceLastCall
      );
    }
  };
}
