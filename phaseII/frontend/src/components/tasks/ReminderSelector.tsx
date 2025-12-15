"use client";

import { useState, useEffect } from "react";
import { Calendar, Clock, Mail, Bell } from "lucide-react";
import { format } from "date-fns";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Calendar as CalendarComponent } from "@/components/ui/calendar";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

type ReminderTiming = "none" | "5min" | "15min" | "1hour" | "1day" | "custom";
type ReminderChannel = "browser" | "email" | "both";

export interface ReminderConfig {
  timing: ReminderTiming;
  channel: ReminderChannel;
  customDate?: Date;
  customTime?: string;
  message?: string;
}

interface ReminderSelectorProps {
  value: ReminderConfig;
  onChange: (config: ReminderConfig) => void;
  dueDate?: string;
}

export function ReminderSelector({
  value,
  onChange,
  dueDate,
}: ReminderSelectorProps) {
  const [enabled, setEnabled] = useState(value.timing !== 'none');
  const [timing, setTiming] = useState<ReminderTiming>(value.timing);
  const [channel, setChannel] = useState<ReminderChannel>(value.channel);
  const [customDate, setCustomDate] = useState<Date | undefined>(value.customDate);
  const [customTime, setCustomTime] = useState(value.customTime || "");
  const [message, setMessage] = useState(value.message || "");
  const [showCustomDatePicker, setShowCustomDatePicker] = useState(false);

  // Sync local state with value prop
  useEffect(() => {
    setEnabled(value.timing !== 'none');
    setTiming(value.timing);
    setChannel(value.channel);
    setCustomDate(value.customDate);
    setCustomTime(value.customTime || "");
    setMessage(value.message || "");
  }, [value]);

  const handleEnabledChange = (checked: boolean) => {
    setEnabled(checked);
    if (!checked) {
      onChange({
        timing: 'none',
        channel,
        customDate,
        customTime,
        message,
      });
    } else {
      onChange({
        timing: timing === 'none' ? '15min' : timing,
        channel,
        customDate,
        customTime,
        message,
      });
    }
  };

  const handleTimingChange = (value: ReminderTiming) => {
    setTiming(value);
    onChange({
      timing: value,
      channel,
      customDate,
      customTime,
      message,
    });
  };

  const handleChannelChange = (value: ReminderChannel) => {
    setChannel(value);
    onChange({
      timing,
      channel: value,
      customDate,
      customTime,
      message,
    });
  };

  const handleCustomDateChange = (date: Date | undefined) => {
    setCustomDate(date);
    setShowCustomDatePicker(false);
    onChange({
      timing,
      channel,
      customDate: date,
      customTime,
      message,
    });
  };

  const handleCustomTimeChange = (time: string) => {
    setCustomTime(time);
    onChange({
      timing,
      channel,
      customDate,
      customTime: time,
      message,
    });
  };

  const handleMessageChange = (msg: string) => {
    setMessage(msg);
    onChange({
      timing,
      channel,
      customDate,
      customTime,
      message: msg,
    });
  };

  return (
    <div className="space-y-4 border rounded-md p-4">
      <div className="flex items-center space-x-2">
        <Checkbox
          id="reminder-enabled"
          checked={enabled}
          onCheckedChange={handleEnabledChange}
        />
        <Label htmlFor="reminder-enabled" className="font-medium">
          Set reminder for this task
        </Label>
      </div>

      {enabled && (
        <>
          {/* Timing Options */}
          <div className="space-y-2">
            <Label className="text-sm font-medium">When to remind</Label>
            <RadioGroup value={timing} onValueChange={handleTimingChange}>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="5min" id="5min" />
                <Label htmlFor="5min" className="font-normal cursor-pointer">
                  5 minutes before due date
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="15min" id="15min" />
                <Label htmlFor="15min" className="font-normal cursor-pointer">
                  15 minutes before due date
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="1hour" id="1hour" />
                <Label htmlFor="1hour" className="font-normal cursor-pointer">
                  1 hour before due date
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="1day" id="1day" />
                <Label htmlFor="1day" className="font-normal cursor-pointer">
                  1 day before due date
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="custom" id="custom" />
                <Label htmlFor="custom" className="font-normal cursor-pointer">
                  Custom date and time
                </Label>
              </div>
            </RadioGroup>
          </div>

          {/* Custom Date/Time Picker */}
          {timing === "custom" && (
            <div className="space-y-2 pl-6">
              <div className="flex gap-2">
                <Popover
                  open={showCustomDatePicker}
                  onOpenChange={setShowCustomDatePicker}
                >
                  <PopoverTrigger asChild>
                    <Button variant="outline" className="w-full">
                      <Calendar className="mr-2 h-4 w-4" />
                      {customDate ? format(customDate, "PPP") : "Pick a date"}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0">
                    <CalendarComponent
                      mode="single"
                      selected={customDate}
                      onSelect={handleCustomDateChange}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>

                <div className="flex items-center gap-2 w-full">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <Input
                    type="time"
                    value={customTime}
                    onChange={(e) => handleCustomTimeChange(e.target.value)}
                    className="w-full"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Channel Options */}
          <div className="space-y-2">
            <Label className="text-sm font-medium">How to remind</Label>
            <RadioGroup value={channel} onValueChange={handleChannelChange}>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="browser" id="browser" />
                <Bell className="h-4 w-4 text-muted-foreground" />
                <Label htmlFor="browser" className="font-normal cursor-pointer">
                  Browser notification
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="email" id="email" />
                <Mail className="h-4 w-4 text-muted-foreground" />
                <Label htmlFor="email" className="font-normal cursor-pointer">
                  Email notification
                </Label>
              </div>
              <div className="flex items-center space-x-2">
                <RadioGroupItem value="both" id="both" />
                <div className="flex gap-1">
                  <Bell className="h-4 w-4 text-muted-foreground" />
                  <Mail className="h-4 w-4 text-muted-foreground" />
                </div>
                <Label htmlFor="both" className="font-normal cursor-pointer">
                  Both browser and email
                </Label>
              </div>
            </RadioGroup>
          </div>

          {/* Custom Message */}
          <div className="space-y-2">
            <Label htmlFor="reminder-message" className="text-sm font-medium">
              Custom message (optional)
            </Label>
            <Textarea
              id="reminder-message"
              placeholder="Add a custom reminder message..."
              value={message}
              onChange={(e) => handleMessageChange(e.target.value)}
              maxLength={500}
              rows={3}
              className="resize-none"
            />
            <p className="text-xs text-muted-foreground text-right">
              {message.length}/500 characters
            </p>
          </div>
        </>
      )}
    </div>
  );
}
