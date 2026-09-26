# Brokerage connection

> **From 3.0** · **Korea Investment & Securities only** · **Reads balances only — it never places orders.**
> Available on iPhone · iPad · Mac · Android.

Golgoru reads your Korea Investment account balances (holdings · quantities · average prices · cash)
and fills the accounts you manage with **Enter my assets**. Besides regular brokerage accounts it finds
and links pension savings, IRP and retirement (DC) accounts too.

Golgoru does not trade for you. Make the trades your adjustment plan suggests **in the Korea Investment app**.
Afterwards, read the balances again in Golgoru and your accounts match the real numbers.

## What you need

| What | Where |
| --- | --- |
| Start with **Enter my assets** | Settings > My assets > Start with (you can't link in Sample mode) |
| App key · app secret | Issued **to you** on KIS Developers — Korea Investment issues **one per account** |
| First 8 digits of the account number | Account details in the Korea Investment app |

## Linking

1. Sign in to **KIS Developers** (Korea Investment's open API portal), apply for API access and get a
   **live** app key and app secret.
2. In Golgoru open **Settings > Brokerage connections > Korea Investment · Live**.
3. Enter the app key, app secret and the first 8 digits of the account number.
4. Turn on **"This key is mine, issued for an account in my own name"** and **save**.
5. Tap **check the connection** — it asks the Korea Investment server for an access token.
6. **Find and link accounts** looks up every account opened with that key (brokerage · pension savings ·
   IRP · retirement DC …). For each one, **link** it to an existing Golgoru account or **add it as a new
   account** — a new account is filled from the balances right away.

If you have several accounts, each has its own app key: use **Add a key group** for the others.
Give each group a name you'll recognise (e.g. ISA · Pension).

You can also start from account editing — it links what it finds to that account and fills it in.

- **iPhone · iPad · Mac**: in **Settings > My assets > Accounts**, **long-press** an account and choose
  **Find and link an account at Korea Investment (Live)**
- **Android**: in **Settings > Edit accounts · holdings**, tap **⋯** next to the account and choose
  **Find and link an account at KIS Live**

## Matching balances again

- Open an account on the **Assets tab**: the top shows the link and when it was last synced. Tap it to see
  what differs from the brokerage (quantities · average prices · cash) — nothing changes until you tap **Apply**.
- In account editing — on iPhone · iPad · Mac long-press the account and choose **Import from linked Korea
  Investment (…) · Pension savings**; on Android tap **⋯** and choose **Import balances from the linked account**.
- If you ran an adjustment plan in the Korea Investment app, open the plan in progress and use **Finish round N
  from brokerage balances** — instead of ticking orders off one by one, it uses what **actually filled**. The round
  is marked done only after you tap **Apply** (if the lookup fails or you just close it, the round stays open).

## Keys and privacy

- The app key, app secret and account number are stored **only on this device** — in the Keychain on iPhone ·
  iPad · Mac (Face ID or the device passcode to read), encrypted with the Android Keystore on Android.
- Balances are read **directly from the device to Korea Investment**. They never pass through a Golgoru
  server, and the developer never receives your keys, accounts or balances.
- The link itself doesn't store your account number — only which key and account type go with which Golgoru account.
- Links stay **on this device**. Keys live only on the device, so a link travelling to another device would
  look connected without a key there. To use it on another device, enter the key on that device.
- **Don't enter someone else's app key.** Handing over or borrowing an app key can count as lending an access
  medium, which Korea's Electronic Financial Transactions Act prohibits.

## What it doesn't do

- Orders or reserved orders — Golgoru never trades for you.
- Brokerages other than Korea Investment, or paper-trading accounts.
- Linking in Sample mode.

The analysis and adjustment plans in Golgoru are for reference only and are not investment advice.
