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

- The top card — days left, **remaining budget**, income and a bar of how it split into spending · to assets · left in the bank.
- Daily average spending and **categories over budget** and by how much.
- Records by day below, and for the current month, repeats still to come.
- Use ‹ › at the top to see earlier months.

## By category

- Spending as **category blocks** — size is share, and a category over budget gets an orange outline.
- Grouped into **Fixed** (the same each month) and **Living** (changes month to month), each with spent / budget.
- **To assets** lists what went to accounts and pockets next to the plan — rows with a repeat show as planned, others as not yet.
- Tap a category for a **6-month bar chart** and its records, and record straight into it.

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
