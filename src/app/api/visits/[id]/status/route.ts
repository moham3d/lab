import { NextRequest, NextResponse } from "next/server"
import { db } from "@/lib/db"

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await request.json()
    const { status } = body

    // Validate status
    const validStatuses = ["OPEN", "IN_PROGRESS", "COMPLETED", "CANCELLED"]
    if (!validStatuses.includes(status)) {
      return NextResponse.json(
        { detail: "Invalid status value" },
        { status: 400 }
      )
    }

    // Check if visit exists
    const visit = await db.visit.findUnique({
      where: { id: params.id },
      include: {
        checkEval: true,
        generalSheet: true,
      }
    })

    if (!visit) {
      return NextResponse.json(
        { detail: "Visit not found" },
        { status: 404 }
      )
    }

    // Validate business rules for status changes
    if (status === "COMPLETED") {
      // Check if both forms are completed before marking as COMPLETED
      if (!visit.checkEval || !visit.generalSheet) {
        return NextResponse.json(
          { 
            detail: "Cannot mark visit as completed. Both nursing and physician assessments must be completed first.",
            missingForms: {
              checkEval: !visit.checkEval,
              generalSheet: !visit.generalSheet
            }
          },
          { status: 400 }
        )
      }
    }

    // Update visit status
    const updatedVisit = await db.visit.update({
      where: { id: params.id },
      data: {
        visitStatus: status,
        updatedAt: new Date(),
      },
      include: {
        patient: true,
        user: true,
        checkEval: true,
        generalSheet: true,
      }
    })

    return NextResponse.json(updatedVisit)
  } catch (error) {
    console.error("Error updating visit status:", error)
    return NextResponse.json(
      { detail: "Internal server error" },
      { status: 500 }
    )
  }
}