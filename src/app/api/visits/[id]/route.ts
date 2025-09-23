import { NextRequest, NextResponse } from "next/server"
import { db } from "@/lib/db"

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params
    const visit = await db.visit.findUnique({
      where: { id },
      include: {
        patient: true,
        user: {
          select: {
            fullName: true,
            username: true,
            role: true,
          },
        },
        checkEval: true,
        generalSheet: true,
      },
    })

    if (!visit) {
      return NextResponse.json(
        { detail: "Visit not found" },
        { status: 404 }
      )
    }

    return NextResponse.json(visit)
  } catch (error) {
    console.error("Error fetching visit:", error)
    return NextResponse.json(
      { detail: "Internal server error" },
      { status: 500 }
    )
  }
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params
    const body = await request.json()
    const { notes, visitStatus } = body

    // Check if visit exists
    const existingVisit = await db.visit.findUnique({
      where: { id },
    })

    if (!existingVisit) {
      return NextResponse.json(
        { detail: "Visit not found" },
        { status: 404 }
      )
    }

    // Update visit
    const updatedVisit = await db.visit.update({
      where: { id },
      data: {
        ...(notes !== undefined && { notes }),
        ...(visitStatus !== undefined && { visitStatus }),
      },
      include: {
        patient: true,
        user: {
          select: {
            fullName: true,
            username: true,
            role: true,
          },
        },
        checkEval: true,
        generalSheet: true,
      },
    })

    return NextResponse.json(updatedVisit)
  } catch (error) {
    console.error("Error updating visit:", error)
    return NextResponse.json(
      { detail: "Internal server error" },
      { status: 500 }
    )
  }
}