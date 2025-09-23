import { NextRequest, NextResponse } from "next/server"
import { db } from "@/lib/db"

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const skip = parseInt(searchParams.get("skip") || "0")
    const limit = parseInt(searchParams.get("limit") || "100")

    const reports = await db.report.findMany({
      skip,
      take: limit,
      include: {
        user: {
          select: {
            id: true,
            fullName: true,
            username: true,
          },
        },
        visit: {
          select: {
            id: true,
            patient: {
              select: {
                fullName: true,
                ssn: true,
              },
            },
          },
        },
      },
      orderBy: {
        createdAt: "desc",
      },
    })

    return NextResponse.json(reports)
  } catch (error) {
    console.error("Error fetching reports:", error)
    return NextResponse.json(
      { detail: "Internal server error" },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { visitId, summary, doctorNotes } = body

    // Validate required fields
    if (!visitId || !summary) {
      return NextResponse.json(
        { detail: "Visit ID and summary are required" },
        { status: 400 }
      )
    }

    // Check if visit exists
    const visit = await db.visit.findUnique({
      where: { id: visitId },
    })

    if (!visit) {
      return NextResponse.json(
        { detail: "Visit not found" },
        { status: 404 }
      )
    }

    // Get user from token (simplified)
    const authHeader = request.headers.get("authorization")
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return NextResponse.json(
        { detail: "Invalid authentication" },
        { status: 401 }
      )
    }

    const token = authHeader.substring(7)
    const userId = Buffer.from(token, 'base64').toString().split(':')[0]

    // Create report
    const report = await db.report.create({
      data: {
        visitId,
        summary,
        doctorNotes: doctorNotes || null,
        createdBy: userId,
      },
      include: {
        user: {
          select: {
            id: true,
            fullName: true,
            username: true,
          },
        },
        visit: {
          select: {
            id: true,
            patient: {
              select: {
                fullName: true,
                ssn: true,
              },
            },
          },
        },
      },
    })

    return NextResponse.json(report, { status: 201 })
  } catch (error) {
    console.error("Error creating report:", error)
    return NextResponse.json(
      { detail: "Internal server error" },
      { status: 500 }
    )
  }
}