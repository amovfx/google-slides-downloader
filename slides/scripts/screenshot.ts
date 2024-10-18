import * as fs from "fs";
import * as path from "path";
import { chromium } from "playwright";

async function getSlideCount(id: string): Promise<number> {
  const response = await fetch(`http://localhost:3000/${id}/count`);
  const data = await response.json();
  return data.count;
}

async function captureScreenshots(id: string) {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  await page.goto(`http://localhost:3000/${id}`);

  const slideCount = await getSlideCount(id);

  // Create the folder for this id
  const outputDir = path.join(
    "/Users/andrew/git/google-slides-downloader/component_renderer",
    id
  );
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  for (let i = 0; i < slideCount; i++) {
    // Wait for the slide to be visible
    await page.waitForSelector('[role="group"][aria-roledescription="slide"]', {
      state: "visible",
    });

    // Take a screenshot and save it in the new folder
    await page.screenshot({
      path: path.join(outputDir, `image_${i + 1}.png`),
      fullPage: true,
    });

    if (i < slideCount - 1) {
      // Perform the drag action to move to the next slide
      await page.mouse.move(
        page.viewportSize()!.width - 50,
        page.viewportSize()!.height / 2
      );
      await page.mouse.down();
      await page.mouse.move(50, page.viewportSize()!.height / 2, { steps: 10 });
      await page.mouse.up();

      // Wait for the transition to complete
      await page.waitForTimeout(1000);
    }
  }

  await browser.close();
}

// Get the id from command line arguments
const id = process.argv[2];

if (!id) {
  console.error("Please provide an id as an argument");
  process.exit(1);
}

captureScreenshots(id).catch(console.error);
