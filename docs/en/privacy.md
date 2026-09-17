# Privacy policy

Golgoru (“the app”) does not store your asset data on our servers.
This page explains what the app handles, where it is kept, and what leaves the device.

> Last updated: 2026-08-21

## What the app handles

### Asset information

Account names, holdings, quantities, average costs, cash balances and target weights.

Depending on how you started, they are stored in one of these places.

| How you started | Where it is stored | Devices |
| --- | --- | --- |
| Sample | Not stored (example data) | All |
| Entered in the app | Your device's storage (on Apple devices also synced to your own iCloud; on Android, to your own Google Drive if you turn device sharing on) | All |
| Google Sheets link (up to 1.0) | Your own Google spreadsheet | iPhone · iPad · Mac |
| Portfolios you built (from 1.3.0) | Your device's storage (mirrored to your own iCloud on Apple devices) | All |

In every case, **nothing is stored on our servers.**

Device storage means the app-only area the platform provides — the app sandbox on Apple devices,
app-private storage on Android (other apps cannot read it, and it is excluded from device backups).

On Apple devices, a ledger entered with “enter my assets” also syncs to **your own iCloud** so your iPhone
and iPad can see it together. We cannot reach that area, and a device not signed in to iCloud does not sync.
On Android this happens **only if you turn device sharing on**, storing the ledger in your own Google Drive as
two files (`golgoru-ledger.json` — accounts and holdings; `golgoru-rebalancing.json` — rebalancing in progress).
It is off by default. The only permission the app asks for is `drive.file`, which lets it see **only the files it
created** — it cannot even tell whether other files in your Drive exist. We cannot reach those files.

### Portfolios you built (from 1.3.0)

A mix you have not bought (its name, holdings, weights and amount) is stored on the device **separately** from
your ledger. On Apple devices it is mirrored to your own iCloud so iPhone, iPad and Mac see the same list;
we cannot reach that area. On Android it stays on the device.

A **share link carries the portfolio after the `#`** in the address. URL fragments **are never sent to a server**,
so nothing is stored on our servers and nothing appears in access logs. It joins the other person's device only
when **they press save**.

### Google account information

**Since 1.2.0 the public app has no Google sign-in.** The Google Sheets link was removed; what follows applies
to version 1.0.

Google sign-in was used only when you chose the Google Sheets link.
**The Android app has no sheet link** — it offers the sample and manual entry only, so the sheet material below
does not apply to Android.

The one place Android asks for a Google sign-in is **turning device sharing on**, and the permission requested
there is `https://www.googleapis.com/auth/drive.file` alone — it reads, creates and edits **only files the app
created**. It does not touch other files in your Drive and cannot list them. Leave sharing off and no sign-in happens.

- Permission requested: `https://www.googleapis.com/auth/spreadsheets.readonly`
  — it **only reads** the spreadsheet you point it at. It never edits or deletes.
- Purpose: reading your assets from your `App_Data_*` sheets to show them in the app.
- The access token is kept only in the device keychain and is never transmitted.
- The app does not list your Google Drive files. You enter the spreadsheet address yourself,
  so no file-search permission is needed.

Golgoru's use and transfer of information received from Google APIs adheres to the
[Google API Services User Data Policy](https://developers.google.com/terms/api-services-user-data-policy),
including the Limited Use requirements.

### Broker API keys

**2.0 removed broker connections.** The public app neither receives nor stores broker API keys and never talks
to a broker's servers. Holdings are entered by you or filled **from a screenshot of your brokerage app** —
the text recognition runs on the device, and the image never leaves it.

If a key saved by a version before 2.0 is still on the device, deleting the app removes it.

The app used broker APIs **for reading balances only**. It never placed orders.

## What leaves the device

The app uses its own serverless functions (Cloudflare Workers) for prices and news.
What is sent is limited to this.

| Feature | What is sent | What is not |
| --- | --- | --- |
| Prices · charts | The holding symbol | Quantities, amounts, accounts |
| Market indicators | The indicator code only | Any asset information |
| News · reports | Holding names, search keywords | Quantities, amounts, accounts |
| ETF search · comparison (1.3.0) | The search term, the symbol | Amounts, weights, what you hold |

**Money figures are never sent to our servers.** As the table shows, what goes out is a symbol and a search term —
never your total, your position values or an account balance. Amounts, currency conversion and weights are all
calculated on the device.

**The exception is your own storage.** A ledger entered with “enter my assets” syncs to **your own iCloud** on
Apple devices, and to **your own Google Drive on Android if you turned device sharing on**, so your devices can
see it together. Both belong to your account and **we cannot reach them.** Without an iCloud sign-in, or with
device sharing off on Android, no sync happens.

**Asset information is never sent to an outside AI (LLM).** Diagnosis, goal suggestions and rebalancing maths are
all rule-based logic inside the app.

The public app has no AI features at all. Since 1.2.0 the app fetches news straight from Google News and opens
articles at their original page — nothing is sent anywhere to be translated or summarized.

**Importing holdings from a screenshot does not transmit the image either.** Reading the text from what you
pasted is done by the operating system on the device (Apple Vision). The image is discarded as soon as it is
read and never stored.

## Keeping and deleting

- Data on the device sits in the app-only area, where other apps cannot read it.
  Apple devices apply file protection, so it is unreadable while the device is locked;
  Android keeps it in app-private storage and excludes it from device backups.
- Settings can delete the local cache and the ledger you entered.
- Deleting the app deletes everything it stored on the device.
- Disconnecting the Google Sheets link (Apple devices only) removes the stored token from the keychain.
  The sheet itself is yours, so the app does not delete it.
- You can revoke the app's access at any time on the
  [Google account permissions page](https://myaccount.google.com/permissions).

## Sharing with third parties

We do not sell or pass your asset information or Google account information to third parties.
The app collects no advertising identifier and carries no analytics SDK.

## Children's privacy

The app is not directed at children under 14 and does not knowingly collect their personal information.

## Investment notice

The analysis and suggestions the app provides are for reference only — they are not investment advice or a
recommendation. Every investment decision, and its outcome, is yours.

## Contact

indus96@gmail.com

## Changes

If this policy changes, the last-updated date on this page is updated, and important changes are announced
inside the app.
