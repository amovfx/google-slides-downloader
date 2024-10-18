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

  for (let i = 0; i < slideCount; i++) {
    // Wait for the slide to be visible
    await page.waitForSelector(".carousel-item", { state: "visible" });

    // Take a screenshot
    await page.screenshot({
      path: `screenshot_${id}_${i + 1}.png`,
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
