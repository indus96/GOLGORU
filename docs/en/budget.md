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

- **Categories** — name, group (fixed · living) and monthly budget, and new categories.
- **Repeating records** — see what repeats; tap to edit, swipe to stop.
- **Export CSV** — a year's records as a file. You choose where it goes.

## Where your records live

- On your device, one file per year. On Apple devices they sync through **your own iCloud** (CloudKit private database) so iPhone, iPad and Mac see the same budget.
- On Android, only if you turn on device sync, they go to a single file, “골고루-가계부.json”, in **your own Google Drive**
  (with `drive.file`, which can see only files this app created).
- Budget records are **never sent to Golgoru's servers, the AI briefing or the community.** See the [privacy policy](privacy.html).
- The budget in the sample is an example. You can change it, but it resets when you reopen the app.

## What it does not do

No card or bank linking, no reading texts or notifications, no AI categorising. Screenshots and memo suggestions keep recording quick enough.
