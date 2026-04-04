import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const { repoUrl } = await req.json();

    if (!repoUrl) {
      return NextResponse.json(
        { error: "Repository URL is required" },
        { status: 400 }
      );
    }

    // Call the FastAPI backend
    const backendUrl = process.env.BACKEND_URL || "http://127.0.0.1:8000";
    
    // We fetch the SSE stream from the FastAPI backend
    const response = await fetch(`${backendUrl}/api/analyze`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: JSON.stringify({ repo_url: repoUrl }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      let errorMessage = `Backend error: ${response.status}`;
      try {
        const errorJson = JSON.parse(errorText);
        if (errorJson.detail) errorMessage = errorJson.detail;
      } catch (e) {
        // use raw text if not json
      }
      return NextResponse.json({ error: errorMessage }, { status: response.status });
    }

    // Proxy the SSE stream back to the client
    return new NextResponse(response.body, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
      },
    });
  } catch (error) {
    console.error("Error in analyze API route:", error);
    return NextResponse.json(
      { error: "Internal server error connecting to analysis engine" },
      { status: 500 }
    );
  }
}
