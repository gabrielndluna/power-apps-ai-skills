# Dayaway ↔ Staff Club sync

Validated design for Dayaway YNSE (2026-07-30).

## Model

- **Source of truth for leave requests (ranges):** `Vacations Tracking (Days)`
- **Mirror into Staff Club timesheets (daily):** `Hours Tracking (Hours)`
- Staff Club does **not** read Dayaway lists. It only shows leave if Hours rows exist.
- **No historical backfill** — only new create/edit/approve/delete from Dayaway.

## Leave types (Dayaway picker)

Exact Staff Club `Task` strings (time-off only):

```
Stat. Holiday
Vacation Paid
Vacation Unpaid
Sick Leave Paid
Sick Leave Unpaid
Bereavement
Jury Duty
Personal Day
```

Stored on Days as `Type_of_leave` and on Hours as `Task` (per day — see below).

## Dual-write keys

On submit, expand the range to **one Hours row per Mon–Fri** (weekends skipped). Public holidays from `colPublic_Holidays` (project-filtered) are included as Hours rows:

| Calendar day | Hours row? | Hours `Task` | Counts toward Days entitlement? |
|--------------|------------|--------------|----------------------------------|
| Weekend | No | — | No |
| Public holiday (Mon–Fri) | Yes | `Stat. Holiday` | Only if leave type is `Stat. Holiday` |
| Other weekday | Yes | selected leave type | Yes (except when leave type is `Stat. Holiday`) |

| Hours field | Value |
|-------------|--------|
| `LOG_ID` / `Title` | `{Days.LOG_ID}_{yyyymmdd}` |
| `Employee` | user email |
| `Date` | that calendar day |
| `Task` | `Stat. Holiday` if date is a project public holiday; else leave type |
| `Standard_time` | `0` |
| `App_Name` | `Dayaway` |
| `ApprovalStatus_1` | same as Days (`Pending` / later Approved/Rejected) |
| `ApproverID_1` | from Excel Employees `Approver Email` |

`Days` on the Vacations Tracking row still uses entitlement rules (Mon–Fri excluding holidays for normal leave; Mon–Fri that **are** holidays when type is `Stat. Holiday`).

## Conflict rule

If Hours already has `Work Day` / `Weekend` / blank Task with `Standard_time > 0` on any Mon–Fri day in the range (including holiday weekdays), Dayaway **blocks** submit and asks the user to clear Staff Club hours first.

## Staffclock weekly grid (YNSE)

When loading a week with missing day rows, Staffclock defaults like weekends:

| Day | Default `Task` | Row chrome | Cost code |
|-----|----------------|------------|-----------|
| Sat/Sun | `Weekend` | Grey | blank |
| Project public holiday (Mon–Fri) | `Stat. Holiday` | Grey | blank |
| Other weekday | `Work Day` | White | selected cost code |

Holidays come from SharePoint `Public_Holidays` (full list). Parse with `DateValue(Trim(Text(Date))) + 1` (SharePoint date offset) and match via `CleanDateKey` (`yyyy-mm-dd`). Weekend wins if a holiday falls on Sat/Sun.

## Connector requirement

Dayaway must include SharePoint list **Hours Tracking (Hours)** (same site as Staff Club). If the packed app opens without it:

1. In Studio, add data → SharePoint → `Hours Tracking (Hours)`
2. Save / export seed, refresh `Dayaway_YNSE/src/*.msapr` if re-packing from YAML

## Mobile UI

Phone-first AutoLayout, Staff Club navy tokens (`RGBA(0, 18, 107)`). Screens: `Vacations Tracking`, `Approvals`. Flights / Power BI deferred from primary chrome.

**Responsive (single UI):** `App.SizeBreakpoints = [680, 900, 1200]`. Below 680px: welcome + balance chips + request cards + bottom FAB to open full-screen submit sheet; Approvals tab hidden. At/above 680px: Approvals tab + New request for managers/desktop. Preview with a phone device or a narrow window so `App.Width < 680` — Scale-to-fit alone on a fixed desktop canvas will not switch chrome.
