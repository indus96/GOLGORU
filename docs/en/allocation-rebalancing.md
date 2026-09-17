# Adjustment plan

> **Works with:** the sample · your own assets
> (editing target weights only when you enter your own assets)

Works out the gap between your target weights and what you actually hold, and shows only
**what to move and how much**. You get there from the “adjustment plan” row on the
[Assets](asset-ranking.md) screen, or “see the adjustment plan” in an account.

## What you see

One card per class. On the bar, **the dark tick is the target and the filled colour is where you are**.

- Above the target it says **trim**; below it, **add** — with the amount.
- The target and current figures **carry amounts** — `Target 35% · ₩17.5M` / `Now 40% · ₩20M`.
  With percentages alone, nothing on screen says 35% of what.
- **Classes inside the range fold into one line** — `Cash target 10% · ₩5M · same as now`.
- The order is fixed, biggest gap first. There is no sort to choose.
- Tapping an adjustment row opens **that holding's screen** — deciding how much to trim means
  looking at today's price.

## One threshold, in one place

**The threshold lives at Settings &gt; My assets &gt; Adjust when off by**, and nowhere else.
The `pp` badge on the Assets screen and the list here use **the same value**.
Set per screen, you end up with “three need adjusting but nothing is marked”.

## One account at a time

Coming in from an account shows **only that account**. Tapping into your brokerage account and
being told about your fund account breaks the thread. Inside an account the holding is pinned down,
so it goes as far as **share counts** — `about 2.5 of 12 shares`. **See the full plan** at the bottom
widens it again.

## After you trade

**The app does not place orders.** Update the **quantity and average cost in account editing** to match
what you bought or sold in your brokerage app. The plan recalculates the moment you do.

## Editing target weights

When you **enter your own assets**, the **account editing** screen changes quantity, average cost,
target weight and cash balance in one place. Open it with **Edit** in the account, or from
Settings &gt; My assets &gt; Accounts.

- Add holdings by search; anything search does not carry (cash · deposits · savings plans · real estate ·
  bonds · funds) is picked from a list.
- **Cash takes a target weight too** — put a target % on the cash row and it counts in the total.
- If you changed target weights, the account has to add up to 100% to save (changing quantities alone has no such limit).
- Holdings with no target still appear, at 0%.
- To move several accounts' targets at once, use **adjust weights across accounts** at the bottom of
  Settings &gt; My assets &gt; Accounts.

## When another device got there first

If the same holding was changed differently on two devices, saving asks **which one to keep**.
Changes to different holdings are already merged, so you are only asked about what really diverged.
You cannot close without choosing — that would leave the edit neither saved nor discarded.

## Rebalancing plan

**The app does not place orders.** It builds a plan of what to buy and sell, and you place the orders
yourself in your brokerage app. Check off what you ran and your holdings and records line up.

### 1. Build the plan

Pick the holdings, choose **how many rounds** (1 · 3 · 5) and **the interval**
(at once · 1 day · 7 days · a month · your own), and it works out quantities and amounts per sell and buy
leg, down to the cash you would have left.

- Sells are worked out first to raise the money, and the buys are filled from it.
- It only adjusts **inside one account**. Nothing moves between accounts.

### 2. Save it → in progress

**Save the plan** and it stays on the adjustment screen as an **in progress** banner. It survives
quitting the app, and tapping the banner reopens it any time.

If you set an interval, a **notification arrives at 9:05 in the morning** on each round's due date.
Tapping it opens that plan (you have to allow notifications once for this).

### 3. Run it and check it off

Place the orders in your brokerage app, come back, and check them.

- Tap **done** on a holding, or **check the whole round** if you ran the round in one go.
- Checking **updates your quantity, average cost and cash** (when you enter your own assets).
  Skip it and your ledger keeps the old quantity, so the next plan is built on holdings that are wrong.
- Average cost is re-weighted on buys only; sells leave it alone. The app cannot know your fill price,
  so it records **the plan's expected price**.
- Check every line in a round and it moves to the next; finish them all and the banner goes away.

### 4. Look back

**Records** on the adjustment screen stacks them by plan. Date, account, count and the sell/buy totals
are folded up; open one and you see the round, price and amount. Scheduled notifications are listed there
too, and tapping one goes to its plan.

Records are kept **on this device only** (checked something by mistake? press and hold to delete).

## What the weight divides by

The denominator for your actual weight is **the account total including its cash**.
Leave cash out and holding a lot of it makes your stock weights look higher than they are.

*This screen works out the gap. You place the orders yourself, at your broker.*
