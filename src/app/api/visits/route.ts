import { NextRequest, NextResponse } from "next/server"
import { db } from "@/lib/db"

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const skip = parseInt(searchParams.get("skip") || "0")
    const limit = parseInt(searchParams.get("limit") || "100")

    const visits = await db.visit.findMany({
      skip,
      take: limit,
      include: {
        patient: {
          select: {
            fullName: true,
            ssn: true,
          },
        },
        user: {
          select: {
            fullName: true,
            username: true,
          },
        },
      },
      orderBy: {
        visitDate: "desc",
      },
    })

    return NextResponse.json(visits)
  } catch (error) {
    console.error("Error fetching visits:", error)
    return NextResponse.json(
      { detail: "Internal server error" },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { patientSsn, notes } = body

    // Validate required fields
    if (!patientSsn) {
      return NextResponse.json(
        { detail: "Patient SSN is required" },
        { status: 400 }
      )
    }

    // Check if patient exists
    const patient = await db.patient.findUnique({
      where: { ssn: patientSsn },
    })

    if (!patient) {
      return NextResponse.json(
        { detail: "Patient not found" },
        { status: 404 }
      )
    }

    // Get user from token (simplified - in production, use proper JWT verification)
    const authHeader = request.headers.get("authorization")
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return NextResponse.json(
        { detail: "Invalid authentication" },
        { status: 401 }
      )
    }

    const token = authHeader.substring(7)
    const userId = Buffer.from(token, 'base64').toString().split(':')[0]

    // Create visit
    const visit = await db.visit.create({
      data: {
        patientSsn,
        notes: notes || null,
        createdBy: userId,
      },
      include: {
        patient: true,
        user: {
          select: {
            fullName: true,
            username: true,
          },
        },
      },
    })

    return NextResponse.json(visit, { status: 201 })
  } catch (error) {
    console.error("Error creating visit:", error)
    return NextResponse.json(
      { detail: "Internal server error" },
      { status: 500 }
    )
  }
}