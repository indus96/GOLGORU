# Budget

> **Works with:** the sample · your own assets · from 4.0.0 (iPhone · iPad · Mac · Android)

The third tab is **Budget**. It is not just a list of what you spent — it shows how the money that came in this month
split into **spending, money sent to your accounts, and what is left in the bank**.
Money sent to savings, pension or brokerage accounts is recorded as **To assets**, so it never mixes with spending.

## Recording

Tap **+** at the bottom right (or + on the Home budget card, or the budget widget).

- **Spending · Income · To assets**, an amount, a memo and a date.
- **Category** — pick it from the chips. Type a memo and it picks the category you used last time for the same memo,
  and offers memo suggestions.
- **Repeat** — none · weekly · monthly · yearly, based on the date you picked (the 31st falls on the last day of shorter months;
  29 February falls on the 28th in other years). Repeated records carry a small tag, and editing one lets you stop the repeat from then on.

## The month

- The top card (a chart from 4.2.0) — spending and a **spending line**: how spending added up day by day, against last month
  (dotted) and your budget (gold dotted), with today marked in the current month. A chip shows how much more or less than
  last month by the same day.
- The income bar — spending · to assets · left in the bank. In a month you spent more than came in, the overspent part shows
  as an **orange dashed** section. Repeating income still to come (like a salary) is hatched.
- **Categories over budget** as chips ("Travel +47%").
- Records by day below, and for the current month, repeats still to come.
- Use ‹ › at the top to see earlier months. **"2026 review"** next to it opens the year in review (below).

## By category

- Spending as **category blocks** — size is share, and a category over budget gets an orange outline.
- Grouped into **Fixed** (the same each month) and **Living** (changes month to month), each with spent / budget.
- **To assets** lists what went to accounts and pockets next to the plan — rows with a repeat show as planned, others as not yet.
- Tap a category for a **12-month bar chart** (six at a time, swipe for earlier months — from 4.2.0) and its records,
  and record straight into it.

## Year in review

> From 4.2.0

Tap **"2026 review"** at the right of the month header. Everything is worked out on your device, from your own budget records only.

- **Summary** — the months counted (from the first month with records; this year up to this month), income and the bar of
  spending · to assets · left, surplus or deficit.
- **Year check** — the share of income sent to assets (with last year's), the categories most over budget, recurring spending for
  the year, and a category with plenty left. Tap one to jump to its section.
- **Month by month** — spending and to-assets bars (the biggest month in orange) and a **dashed income line** (from 4.4.0).
  **Tap a month** for its income, top categories, money sent to assets and big expenses, and "Open month N in Budget".
- **Income** (from 4.4.0) — the year's total, monthly average and change from last year, income **by category** (salary, bonus …)
  with shares, and a **monthly** chart stacked by category. Occasional income such as a bonus tells you which months it came in.
  Tap a month for its categories and entries, or a category for its 12 months.
- **Budget check** — the budget in the middle, **under budget** to the left, **over budget** to the right (in money, not ratios).
  The yearly budget is today's monthly budget × the months counted.
- **Shares and big expenses** — fixed · living · optional · occasional, recurring spending, the five biggest expenses.
- **Year over year** — when two or more years have records (up to four): income, spending, to assets, saving rate and the categories
  that changed most. A year still running is scaled from year-to-date to 12 months.
- **Budget suggestions** — after three months, categories whose monthly average is far from the budget. **Pick the ones to change
  and edit the amounts**, then "Change N picked budgets" — after you confirm, they apply from this month.
- **Month × category table** — at the bottom, as a popup.
- On wide Mac and iPad (and Android tablet) screens, the summary and checks sit on the left and the picked section on the right.

## Pockets

Pockets are envelopes for a purpose — travel, gifts, the car.

- Choose the **categories that fill it** (To assets categories) and **the ones that draw from it** (spending categories), plus a starting balance and date.
- Balance = starting balance + money in − money spent. Each pocket shows this year's in and out and its balance.
- **Check against the bank** — enter your bank balance and it shows only the difference from the pocket total (the number stays on this device).

## Import from card screenshots

**Import from card screenshots** on the Budget tab → screenshots of a card or budgeting app's transaction list (several at once),
a file on Mac, or paste.

- It reads date, merchant and amount lines into a list. Turn rows on or off, change categories, then **Save N**.
- Across several screenshots, dates carry over and overlapping rows are counted once.
- Rows you **already recorded** (same day, same amount) are left off.
- The text is read **on your device** (Apple Vision on Apple devices, the on-device ML Kit model on Android). Images are never sent or stored.
- If a card app marks a refund only with the word for "cancelled" (no minus sign), it may read as spending — just turn that row off.

## Home and widget

- The **budget card** on Home — this month's income, spending, to assets and left in the bank, with + to record.
- The **budget widget** — remaining budget (or spending, without a budget) and a bar. Small opens a new record; wider sizes show your
  top three categories as chips that record into that category. Large (iPhone · iPad · Mac) adds category progress and recent records.
  **It is the only Golgoru widget that shows amounts** — other people can see a home screen, so placing it is up to you ([Home › Home screen widget](dashboard.html)).

## Settings › Budget

From 4.1.0 the first screen is a short index — tap to go one step in (on wide Mac and iPad screens it opens as a popup).

- **Categories · budgets** — pick spending, to assets or income at the top; spending is grouped (fixed, living, optional, occasional).
  Change a name, group or monthly budget, or add a category. Hidden categories are folded under "Hidden" at the bottom.
- **Repeating records** — see what repeats; tap to edit, swipe to stop.
- **Move · backup** — see "Moving to another device" below.
- **CSV import · export** — a year's records as a CSV file, and CSV import (below).

## Moving to another device · importing

> From 4.1.0

- **Create move file** — records, categories, budgets, repeats and pockets in one file (.json) you save or send where you like.
  Devices on the same Apple account already stay in step through iCloud, so this is for **iPhone ↔ Android** or a separate backup.
- **Import move file** — pick the file and it first shows the period, records, those already here, categories, repeats and pockets.
  **Merge** keeps everything already here: for the same record the later edit wins, and default categories just set up on a new device
  take the budgets and names from the old one. Importing twice does not add rows twice.
- **Import from CSV** — Golgoru's own CSV goes straight in; for another budgeting app it guesses the date, amount, memo, category and
  type columns, which you can change. Korean Excel CSVs (CP949) are read too. Rows go through the same review as screenshot import;
  rows already recorded and transfers (card bills) start unticked. Save Excel files (.xlsx) as CSV first. A CSV holds records only,
  so budgets, repeats and pockets do not move.
- Files are read and written on your device only — never sent to Golgoru's servers.

## Where your records live

- On your device, one file per year. On Apple devices they sync through **your own iCloud** (CloudKit private database) so iPhone, iPad and Mac see the same budget.
- On Android, only if you turn on device sync, they go to a single file, “골고루-가계부.json”, in **your own Google Drive**
  (with `drive.file`, which can see only files this app created).
- Budget records are **never sent to Golgoru's servers, the AI briefing or the community.** See the [privacy policy](privacy.html).
- The budget in the sample is an example. You can change it, but it resets when you reopen the app.

## What it does not do

No card or bank linking, no reading texts or notifications, no AI categorising. Screenshots and memo suggestions keep recording quick enough.
