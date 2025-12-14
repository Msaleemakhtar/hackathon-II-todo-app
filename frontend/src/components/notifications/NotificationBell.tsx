"use client";

import { useState } from "react";
import { Bell, Clock, Trash2, X } from "lucide-react";
import { format, formatDistanceToNow } from "date-fns";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useNotifications } from "@/hooks/useNotifications";
import { cn } from "@/lib/utils";

export function NotificationBell() {
  const {
    reminders,
    upcomingCount,
    isLoading,
    deleteReminder,
    snoozeReminder,
    isDeleting,
    isSnoozing,
  } = useNotifications();

  const [open, setOpen] = useState(false);

  const handleDelete = (id: number) => {
    deleteReminder(id);
  };

  const handleSnooze = (id: number, minutes: number) => {
    snoozeReminder({ id, minutes });
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="relative"
          aria-label="Notifications"
        >
          <Bell className="h-5 w-5" />
          {upcomingCount > 0 && (
            <Badge
              variant="destructive"
              className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-xs"
            >
              {upcomingCount > 99 ? "99+" : upcomingCount}
            </Badge>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80 p-0" align="end">
        <div className="flex items-center justify-between border-b px-4 py-3">
          <h3 className="font-semibold">Reminders</h3>
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6"
            onClick={() => setOpen(false)}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        {isLoading ? (
          <div className="p-8 text-center text-sm text-muted-foreground">
            Loading reminders...
          </div>
        ) : reminders.length === 0 ? (
          <div className="p-8 text-center">
            <Bell className="mx-auto h-12 w-12 text-muted-foreground/50 mb-3" />
            <p className="text-sm text-muted-foreground">
              No upcoming reminders
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Set reminders when creating or editing tasks
            </p>
          </div>
        ) : (
          <ScrollArea className="max-h-[400px]">
            <div className="divide-y">
              {reminders.map((reminder) => (
                <div
                  key={reminder.id}
                  className="p-4 hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <Clock className="h-3.5 w-3.5 text-muted-foreground flex-shrink-0" />
                        <span className="text-sm font-medium truncate">
                          Task #{reminder.task_id}
                        </span>
                      </div>

                      {reminder.message && (
                        <p className="text-sm text-muted-foreground mb-2 line-clamp-2">
                          {reminder.message}
                        </p>
                      )}

                      <div className="flex flex-col gap-1 text-xs text-muted-foreground">
                        <div>
                          {format(new Date(reminder.remind_at), "PPp")}
                        </div>
                        <div>
                          {formatDistanceToNow(new Date(reminder.remind_at), {
                            addSuffix: true,
                          })}
                        </div>
                        <div className="flex items-center gap-1">
                          <Badge variant="outline" className="text-xs">
                            {reminder.channel}
                          </Badge>
                          {reminder.snoozed_until && (
                            <Badge variant="secondary" className="text-xs">
                              Snoozed
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="flex flex-col gap-1">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8"
                        onClick={() => handleSnooze(reminder.id, 15)}
                        disabled={isSnoozing}
                        title="Snooze for 15 minutes"
                      >
                        <Clock className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 text-destructive hover:text-destructive"
                        onClick={() => handleDelete(reminder.id)}
                        disabled={isDeleting}
                        title="Cancel reminder"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        )}

        {reminders.length > 0 && (
          <div className="border-t px-4 py-2 text-center">
            <p className="text-xs text-muted-foreground">
              {upcomingCount} upcoming {upcomingCount === 1 ? "reminder" : "reminders"}
            </p>
          </div>
        )}
      </PopoverContent>
    </Popover>
  );
}
