import { NextResponse } from "next/server";

import { getSlideData } from "@/app/[id]/actions";

export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const slides = await getSlideData(params.id);
    return NextResponse.json({ count: slides.length });
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to fetch slide data" },
      { status: 500 }
    );
  }
}
