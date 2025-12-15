# Data Model: Advanced Features & Optimization

**Feature**: Advanced Features & Optimization - Time Reminders, Notifications, Performance, UX, Monitoring & Analytics  
**Branch**: `005-advanced-features-optimization`  
**Input**: Feature specification from `/specs/005-advanced-features-optimization/spec.md`  

## Entity: Reminder

Represents a scheduled notification for a task.

### Attributes
- `id`: int (Primary Key, Auto-increment)
- `task_id`: int (Foreign Key to tasks.id, CASCADE delete)
- `user_id`: str (Foreign Key to users.id, CASCADE delete, indexed)
- `remind_at`: datetime (When to send the reminder, indexed)
- `channel`: str (Values: "browser", "email", or "both"; max length: 20)
- `is_sent`: bool (Whether the reminder has been sent, indexed, default: false)
- `sent_at`: Optional[datetime] (When the reminder was sent)
- `message`: Optional[str] (Custom message for the reminder, max length: 500)
- `snoozed_until`: Optional[datetime] (When the reminder is snoozed until)
- `created_at`: datetime (When the reminder was created, default: now())
- `updated_at`: datetime (When the reminder was last updated, default: now())

### Relationships
- `task`: One-to-Many with Task model (back_populates: "reminders")
- `user`: One-to-Many with User model (back_populates: "reminders")

### Validation Rules
- `task_id` must reference an existing task for the user
- `remind_at` must be in the future (not in the past)
- `channel` must be one of: "browser", "email", "both"
- `message` cannot exceed 500 characters

### Lifecycle
- Created when user sets a reminder for a task
- Can be snoozed, marked as sent, or cancelled
- Automatically marked as sent after successful delivery (to prevent duplicates)

### Timezone Handling
- Store times in UTC server-side
- Convert to user's current timezone for display and reminders

### Indexes
- `ix_reminders_task_id`: On `task_id`
- `ix_reminders_user_id`: On `user_id`
- `ix_reminders_remind_at`: On `remind_at`
- `ix_reminders_is_sent`: On `is_sent`
- `ix_reminders_pending`: On `(is_sent, remind_at)`

## Entity: WebVital

Represents a performance metric measurement for monitoring Core Web Vitals.

### Attributes
- `id`: int (Primary Key, Auto-increment)
- `name`: str (Name of the metric: CLS, FID, FCP, LCP, TTFB)
- `value`: float (Value of the metric)
- `rating`: str (Rating: "good", "needs-improvement", "poor")
- `user_id`: Optional[str] (User ID if metric is user-specific)
- `timestamp`: datetime (When the metric was recorded, default: now())

### Validation Rules
- `name` must be one of: "CLS", "FID", "FCP", "LCP", "TTFB"
- `rating` must be one of: "good", "needs-improvement", "poor"
- `value` must be a non-negative number

### Purpose
- Aggregate performance data to identify degradation patterns
- Enable monitoring and alerting on performance issues

## Entity: AnalyticsEvent

Represents a user interaction event for analytics tracking.

### Attributes
- `id`: int (Primary Key, Auto-increment)
- `event_name`: str (Name of the event: e.g., "task_created", "task_completed")
- `properties`: JSON (Key-value pairs with additional event properties)
- `user_id`: Optional[str] (User ID if event is user-specific)
- `timestamp`: datetime (When the event occurred, default: now())

### Validation Rules
- `event_name` cannot be empty
- `properties` must be valid JSON object
- `user_id` format must be valid if provided

### Purpose
- Track feature usage and user behavior patterns
- Enable business intelligence and user experience analysis

### Privacy Considerations
- No personally identifiable information (PII) should be stored in properties
- Must respect user consent for tracking

## Entity: CacheEntry

Represents cached API response data for performance optimization.

### Attributes
- `cache_key`: str (Primary Key, Unique identifier for the cached data)
- `cached_data`: JSON (The actual cached data)
- `ttl_seconds`: int (Time-to-live in seconds from creation)
- `created_at`: datetime (When the cache entry was created, default: now())
- `expires_at`: datetime (When the cache entry expires, computed)

### Lifecycle
- Created on first request for data that needs caching
- Served until TTL expires
- Invalidated when underlying data changes

### Purpose
- Reduce database load for frequently accessed data
- Improve response times for cached content
- Implement configurable TTL for different data types

## Entity: TaskOrder

Represents user-defined task sorting position for drag-and-drop functionality.

### Attributes
- `task_id`: int (Primary Key, Foreign Key to tasks.id)
- `user_id`: str (Foreign Key to users.id)
- `sort_order`: int (Position index for ordering tasks)
- `updated_at`: datetime (Last modification timestamp)

### Relationships
- `task`: One-to-One with Task model

### Purpose
- Persist custom task ordering from drag-and-drop
- Enable users to reorder tasks via drag-and-drop

### Validation Rules
- `sort_order` must be a non-negative integer
- Each `task_id` can only have one entry per user
- Order positions should be consecutive without gaps

## Database Migration Requirements

The new entities require the following database migrations:

### Reminder Table
- Create reminders table with all specified fields and relationships
- Create indexes for efficient querying: user_id, task_id, remind_at, is_sent
- Set up CASCADE delete for task and user foreign keys

### Additional Indexes for Performance
- Index on tasks table for optimized queries with multiple filters
- GIN index for full-text search capabilities (if needed)

## Data Integrity & Validation

### Referential Integrity
- Foreign keys maintain referential integrity
- CASCADE deletes remove related data appropriately
- Prevent orphaned records

### Constraints
- Appropriate NOT NULL constraints for required fields
- UNIQUE constraints where needed
- Proper data types to prevent invalid values

## Security Considerations

### Data Isolation
- All queries must be scoped to authenticated user's data
- User ID from JWT token, not path parameter, used for data access

### Sensitive Data
- Cache entries must remain user-specific and not shared across sessions
- Analytics events should not contain PII
- Notification messages should not expose sensitive task information

## Performance Considerations

### Indexing Strategy
- Indexes on frequently queried fields: user_id, status, priority, due_date
- Indexes to support reminder processing: remind_at, is_sent
- Composite indexes for common multi-field queries

### Partitioning
- Consider partitioning reminder table by date for performance with large datasets
- Archive old analytics events periodically to maintain performance

## Migration Path

1. Create new tables with proper foreign key relationships
2. Migrate existing data if needed
3. Add indexes to optimize queries
4. Update application code to use new entities
5. Test all relationships and constraints
6. Implement caching layer using CacheEntry model