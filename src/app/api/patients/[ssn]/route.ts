import { NextRequest, NextResponse } from "next/server"
import { db } from "@/lib/db"

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ ssn: string }> }
) {
  try {
    const { ssn } = await params

    const patient = await db.patient.findUnique({
      where: { ssn },
    })

    if (!patient) {
      return NextResponse.json(
        { detail: "Patient not found" },
        { status: 404 }
      )
    }

    return NextResponse.json(patient)
  } catch (error) {
    console.error("Error fetching patient:", error)
    return NextResponse.json(
      { detail: "Internal server error" },
      { status: 500 }
    )
  }
}