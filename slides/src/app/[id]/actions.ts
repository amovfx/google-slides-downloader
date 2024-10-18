"use server";

import { promises as fs } from "fs";
import yaml from "js-yaml";
import path from "path";

export async function getSlideData(id: string) {
  const filePath = path.join(process.cwd(), `src/data/${id}/manifest.yml`);
  const fileContents = await fs.readFile(filePath, "utf8");
  return yaml.load(fileContents) as Array<{
    title: string;
    subtitle: string;
    content: string | string[];
    image: string;
    imagePosition: "left" | "right";
  }>;
}
