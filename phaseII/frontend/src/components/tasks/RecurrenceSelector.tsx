"use client";

import { useState, useEffect } from 'react';
import { Label } from '@/components/ui/label';

export interface RecurrencePattern {
  frequency: 'daily' | 'weekly' | 'monthly' | 'yearly' | 'none';
  interval: number;
  daysOfWeek?: number[]; // For weekly: [0=Monday, 1=Tuesday, ..., 6=Sunday]
  dayOfMonth?: number; // For monthly: 1-31
  endType: 'never' | 'date' | 'count';
  endDate?: Date;
  count?: number;
}

interface RecurrenceSelectorProps {
  value?: RecurrencePattern;
  onChange: (pattern: RecurrencePattern) => void;
}

const WEEKDAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const RRULE_WEEKDAYS = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'];

export function RecurrenceSelector({ value, onChange }: RecurrenceSelectorProps) {
  const [pattern, setPattern] = useState<RecurrencePattern>(
    value || {
      frequency: 'none',
      interval: 1,
      daysOfWeek: [],
      endType: 'never',
    }
  );

  useEffect(() => {
    if (value) {
      setPattern(value);
    }
  }, [value]);

  const updatePattern = (updates: Partial<RecurrencePattern>) => {
    const newPattern = { ...pattern, ...updates };
    setPattern(newPattern);
    onChange(newPattern);
  };

  const toggleWeekday = (day: number) => {
    const current = pattern.daysOfWeek || [];
    const updated = current.includes(day)
      ? current.filter(d => d !== day)
      : [...current, day].sort();
    updatePattern({ daysOfWeek: updated });
  };

  const getPreviewText = (): string => {
    if (pattern.frequency === 'none') {
      return 'Does not repeat';
    }

    let text = 'Repeats ';

    // Frequency and interval
    if (pattern.interval === 1) {
      text += pattern.frequency;
    } else {
      text += `every ${pattern.interval} ${pattern.frequency === 'daily' ? 'days' :
                pattern.frequency === 'weekly' ? 'weeks' :
                pattern.frequency === 'monthly' ? 'months' : 'years'}`;
    }

    // Weekly: days of week
    if (pattern.frequency === 'weekly' && pattern.daysOfWeek && pattern.daysOfWeek.length > 0) {
      const dayNames = pattern.daysOfWeek.map(d => WEEKDAY_NAMES[d]).join(', ');
      text += ` on ${dayNames}`;
    }

    // Monthly: day of month
    if (pattern.frequency === 'monthly' && pattern.dayOfMonth) {
      text += ` on day ${pattern.dayOfMonth}`;
    }

    // End condition
    if (pattern.endType === 'date' && pattern.endDate) {
      text += ` until ${pattern.endDate.toLocaleDateString()}`;
    } else if (pattern.endType === 'count' && pattern.count) {
      text += ` for ${pattern.count} times`;
    }

    return text;
  };

  return (
    <div className="space-y-4">
      {/* Frequency Selection */}
      <div>
        <Label htmlFor="frequency">Repeats</Label>
        <select
          id="frequency"
          className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={pattern.frequency}
          onChange={(e) => updatePattern({
            frequency: e.target.value as RecurrencePattern['frequency'],
            daysOfWeek: [],
            dayOfMonth: undefined
          })}
        >
          <option value="none">Does not repeat</option>
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
          <option value="yearly">Yearly</option>
        </select>
      </div>

      {pattern.frequency !== 'none' && (
        <>
          {/* Interval */}
          <div>
            <Label htmlFor="interval">Every</Label>
            <div className="flex items-center gap-2 mt-1">
              <input
                id="interval"
                type="number"
                min="1"
                max="99"
                className="w-20 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={pattern.interval}
                onChange={(e) => updatePattern({ interval: parseInt(e.target.value) || 1 })}
              />
              <span className="text-gray-700">
                {pattern.interval === 1 ? pattern.frequency :
                  pattern.frequency === 'daily' ? 'days' :
                  pattern.frequency === 'weekly' ? 'weeks' :
                  pattern.frequency === 'monthly' ? 'months' : 'years'}
              </span>
            </div>
          </div>

          {/* Weekly: Days of Week */}
          {pattern.frequency === 'weekly' && (
            <div>
              <Label>Repeat on</Label>
              <div className="flex flex-wrap gap-2 mt-2">
                {WEEKDAY_NAMES.map((day, index) => (
                  <button
                    key={day}
                    type="button"
                    className={`px-3 py-2 rounded-md border transition-colors ${
                      (pattern.daysOfWeek || []).includes(index)
                        ? 'bg-blue-500 text-white border-blue-500'
                        : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                    }`}
                    onClick={() => toggleWeekday(index)}
                  >
                    {day.slice(0, 3)}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Monthly: Day of Month */}
          {pattern.frequency === 'monthly' && (
            <div>
              <Label htmlFor="dayOfMonth">Day of month</Label>
              <input
                id="dayOfMonth"
                type="number"
                min="1"
                max="31"
                className="w-24 mt-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={pattern.dayOfMonth || 1}
                onChange={(e) => updatePattern({ dayOfMonth: parseInt(e.target.value) || 1 })}
              />
            </div>
          )}

          {/* End Condition */}
          <div>
            <Label htmlFor="endType">Ends</Label>
            <select
              id="endType"
              className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={pattern.endType}
              onChange={(e) => updatePattern({
                endType: e.target.value as RecurrencePattern['endType'],
                endDate: undefined,
                count: undefined
              })}
            >
              <option value="never">Never</option>
              <option value="date">On date</option>
              <option value="count">After occurrences</option>
            </select>
          </div>

          {/* End Date */}
          {pattern.endType === 'date' && (
            <div>
              <Label htmlFor="endDate">End date</Label>
              <input
                id="endDate"
                type="date"
                className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={pattern.endDate?.toISOString().split('T')[0] || ''}
                onChange={(e) => updatePattern({ endDate: e.target.value ? new Date(e.target.value) : undefined })}
              />
            </div>
          )}

          {/* Count */}
          {pattern.endType === 'count' && (
            <div>
              <Label htmlFor="count">Number of occurrences</Label>
              <input
                id="count"
                type="number"
                min="1"
                max="999"
                className="w-32 mt-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={pattern.count || 1}
                onChange={(e) => updatePattern({ count: parseInt(e.target.value) || 1 })}
              />
            </div>
          )}

          {/* Preview */}
          <div className="pt-2 border-t">
            <p className="text-sm text-gray-600 font-medium">Preview</p>
            <p className="text-sm text-gray-800 mt-1">{getPreviewText()}</p>
          </div>
        </>
      )}
    </div>
  );
}

/**
 * Convert RecurrencePattern to RRULE string format
 */
export function patternToRRule(pattern: RecurrencePattern, startDate?: Date): string | null {
  if (pattern.frequency === 'none') {
    return null;
  }

  const parts: string[] = [];

  // Frequency
  const freqMap = {
    daily: 'DAILY',
    weekly: 'WEEKLY',
    monthly: 'MONTHLY',
    yearly: 'YEARLY',
  };
  parts.push(`FREQ=${freqMap[pattern.frequency]}`);

  // Interval
  if (pattern.interval > 1) {
    parts.push(`INTERVAL=${pattern.interval}`);
  }

  // Weekly: Days of week
  if (pattern.frequency === 'weekly' && pattern.daysOfWeek && pattern.daysOfWeek.length > 0) {
    const days = pattern.daysOfWeek.map(d => RRULE_WEEKDAYS[d]).join(',');
    parts.push(`BYDAY=${days}`);
  }

  // Monthly: Day of month
  if (pattern.frequency === 'monthly' && pattern.dayOfMonth) {
    parts.push(`BYMONTHDAY=${pattern.dayOfMonth}`);
  }

  // End condition
  if (pattern.endType === 'date' && pattern.endDate) {
    const endStr = pattern.endDate.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
    parts.push(`UNTIL=${endStr}`);
  } else if (pattern.endType === 'count' && pattern.count) {
    parts.push(`COUNT=${pattern.count}`);
  }

  return parts.join(';');
}

/**
 * Parse RRULE string to RecurrencePattern
 */
export function rruleToPattern(rrule: string): RecurrencePattern {
  const pattern: RecurrencePattern = {
    frequency: 'none',
    interval: 1,
    endType: 'never',
  };

  if (!rrule) {
    return pattern;
  }

  // Remove RRULE: prefix if present
  const ruleString = rrule.startsWith('RRULE:') ? rrule.substring(6) : rrule;
  const parts = ruleString.split(';');

  for (const part of parts) {
    const [key, value] = part.split('=');

    switch (key) {
      case 'FREQ':
        pattern.frequency = value.toLowerCase() as RecurrencePattern['frequency'];
        break;
      case 'INTERVAL':
        pattern.interval = parseInt(value);
        break;
      case 'BYDAY':
        pattern.daysOfWeek = value.split(',').map(day => RRULE_WEEKDAYS.indexOf(day)).filter(i => i >= 0);
        break;
      case 'BYMONTHDAY':
        pattern.dayOfMonth = parseInt(value);
        break;
      case 'UNTIL':
        pattern.endType = 'date';
        pattern.endDate = new Date(value);
        break;
      case 'COUNT':
        pattern.endType = 'count';
        pattern.count = parseInt(value);
        break;
    }
  }

  return pattern;
}
