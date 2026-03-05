# Auto-publish Pins from your RSS feed

Connect RSS feeds to your Pinterest business account to automatically create Pins from the content on your website. We can create Pins for each image in your RSS feed, including items with multiple images or webpages with multiple images.

## Before you get started

Here are a few things to know before you get started:

- You can add as many RSS feeds as you want, as long as they match your claimed website.
- Each feed can publish Pins to a different board. If you select a secret board, your Pins will not be seen by people on Pinterest.
- When you update your RSS feed, your content will be added to your boards as Pins within 24 hours.
- The oldest content on your RSS feed will be published first.
- As your RSS feed is updated, Pins will be created with a limit of up to 200 Pins per day.

## Connect your RSS feed

1. Log in to your **Pinterest business account**.
2. Click the **▾** icon at the top-right corner to open your menu.
3. Click **Settings**.
4. Select **Create Pins in bulk** from the menu at the left.
5. Under **Auto-publish**, click **Connect RSS feed**.
6. Paste your RSS feed URL into the field. (This option will only appear if you have a claimed website.)
7. Below **Save Pins to**, click **▾** to choose a board.
8. Click **Save**.

### Get your RSS feed URL

- **Per domain:** `https://YOUR_DEPLOYED_DOMAIN/rss/domain/DOMAIN_ID`  
  Example: `https://yourapp.com/rss/domain/5`
- Or from **Admin → Domains** → click the Pinterest button (📌) on a domain row to copy the URL.

> **Note:** The feed must be reachable from the internet. Deploy your app (e.g. via Cloudflare, your domain) so the URL works. `localhost` will not work with Pinterest.

## RSS feed specs

- We support **RSS 2.\*** and **RSS 1.\* (RDF)** formats. We currently do not support Atom.
- Make sure your RSS feed page content is in XML format.
- Use a good quality image: your Pins will be taken from the `<image>`, `<enclosure>`, and `<media:content>` tags under each `<item>` tag.
- Your Pin's title and description will be created from the `<title>` and `<description>` tags under each `<item>`.
- Each `<item>` requires a link to your claimed domain.

## RSS feed error messages

| Error message | Suggested action |
|---------------|------------------|
| RSS feed already exists | Try to add a different feed |
| RSS feed cannot be fetched | Make sure the feed URL can be opened (deploy your app, don't use localhost) |
| RSS feed cannot be parsed | Check that the feed you provided is a valid RSS feed in XML format |
| RSS feed unknown format | Make sure your RSS feed is RSS 2.\* or RSS 1.\* format |
| Links in the RSS feed are not under the claimed domain | Check all the links in your feed match your claimed domain (e.g. `yourblog.com/article/123.html`) |

## App-specific notes

- Only articles with a **pin image** (generated via the P button) appear in the feed.
- No Pinterest API key or app needed.
