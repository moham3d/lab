import { NextRequest, NextResponse } from "next/server"
import { db } from "@/lib/db"

export async function GET(request: NextRequest) {
  try {
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

    // Verify user exists and has NURSE role
    const user = await db.user.findUnique({
      where: { id: userId },
      select: { role: true }
    })

    if (!user || user.role !== "NURSE") {
      return NextResponse.json(
        { detail: "Access denied. Nurse role required." },
        { status: 403 }
      )
    }

    // Get current visits (OPEN or IN_PROGRESS) for this nurse only
    const visits = await db.visit.findMany({
      where: {
        createdBy: userId,
        visitStatus: {
          in: ["OPEN", "IN_PROGRESS"]
        }
      },
      include: {
        patient: {
          select: {
            fullName: true,
            ssn: true,
            mobileNumber: true,
            dateOfBirth: true,
            gender: true,
          },
        },
        checkEval: {
          select: {
            id: true,
            createdAt: true,
          },
        },
        generalSheet: {
          select: {
            id: true,
            createdAt: true,
          },
        },
      },
      orderBy: {
        visitDate: "desc",
      },
    })

    return NextResponse.json(visits)
  } catch (error) {
    console.error("Error fetching nurse's current visits:", error)
    return NextResponse.json(
      { detail: "Internal server error" },
      { status: 500 }
    )
  }
}