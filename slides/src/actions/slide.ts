import fs from "fs/promises";
import path from "path";

export async function getImagePath(index: number): Promise<string> {
  "use server";
  const imageDir = path.join(process.cwd(), "public/images/01_Intro/");
  const files = await fs.readdir(imageDir);
  const imageFiles = files.filter((file) =>
    /\.(jpg|jpeg|png|gif)$/i.test(file)
  );
  console.log(imageFiles);

  if (index < imageFiles.length) {
    return `/images/01_Intro/${imageFiles[index]}`;
  }
  return "/placeholder-image.jpg";
}
